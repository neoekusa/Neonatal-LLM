from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from _model_labels import standardize_model_label
from _paths import RAW_SCORES, RAW_TAXONOMY


SCORE_ID_COLUMNS = ["Number", "RealAnswer"]
TAXONOMY_RENAME = {
    "Q No": "Q_No",
    "Knowledge Dimension": "Knowledge",
    "Cognitive Process": "Cognitive",
    "Reasoning  Complexity": "Complexity",
    "Clinical Risk": "Risk",
    "Difficulty": "Difficulty",
    "Universal Task Category": "Task",
}
TAXONOMY_REQUIRED_COLUMNS = [
    "Q No",
    "Main Domain",
    "Subdomain",
    "Knowledge Dimension",
    "Cognitive Process",
    "Reasoning  Complexity",
    "Clinical Risk",
    "Difficulty",
    "Main Guideline",
    "Universal Task Category",
]


@dataclass(frozen=True)
class DataAudit:
    scores_path: Path
    taxonomy_path: Path
    n_questions: int
    n_models: int
    processing_needed: str


def clean_category(series: pd.Series) -> pd.Series:
    return (
        series.astype(str)
        .str.strip()
        .str.replace(" ", "_", regex=False)
        .str.replace(".", "", regex=False)
        .str.replace("/", "_", regex=False)
    )


def read_scores(path: Path = RAW_SCORES) -> pd.DataFrame:
    scores = pd.read_csv(path)
    scores.columns = [col.strip() for col in scores.columns]
    return scores


def read_taxonomy(path: Path = RAW_TAXONOMY) -> pd.DataFrame:
    taxonomy = pd.read_csv(path)
    taxonomy.columns = [col.strip() for col in taxonomy.columns]
    return taxonomy


def model_columns(scores: pd.DataFrame) -> list[str]:
    return [col for col in scores.columns if col not in SCORE_ID_COLUMNS]


def validate_raw_data(scores: pd.DataFrame | None = None, taxonomy: pd.DataFrame | None = None) -> DataAudit:
    scores = read_scores() if scores is None else scores
    taxonomy = read_taxonomy() if taxonomy is None else taxonomy

    missing_score_cols = [col for col in SCORE_ID_COLUMNS if col not in scores.columns]
    missing_tax_cols = [col for col in TAXONOMY_REQUIRED_COLUMNS if col not in taxonomy.columns]
    if missing_score_cols:
        raise ValueError(f"Scores CSV is missing required columns: {missing_score_cols}")
    if missing_tax_cols:
        raise ValueError(f"Taxonomy CSV is missing required columns: {missing_tax_cols}")

    models = model_columns(scores)
    if not models:
        raise ValueError("Scores CSV does not contain model answer columns.")

    score_ids = set(scores["Number"].astype(int))
    tax_ids = set(taxonomy["Q No"].astype(int))
    if score_ids != tax_ids:
        only_scores = sorted(score_ids - tax_ids)
        only_tax = sorted(tax_ids - score_ids)
        raise ValueError(
            "Question IDs differ between scores and taxonomy. "
            f"Only in scores: {only_scores}; only in taxonomy: {only_tax}"
        )

    processing_needed = (
        "No permanent processed dataset is required. The scripts only need in-memory "
        "processing: trim headers/answers, reshape scores from wide to long, compute "
        "Correct/Failure, merge taxonomy by question ID, and clean categorical labels "
        "for statsmodels formulas."
    )
    return DataAudit(
        scores_path=Path(RAW_SCORES),
        taxonomy_path=Path(RAW_TAXONOMY),
        n_questions=len(scores),
        n_models=len(models),
        processing_needed=processing_needed,
    )


def load_long_analysis_df(standardize_models: bool = False) -> pd.DataFrame:
    scores = read_scores()
    taxonomy = read_taxonomy()
    validate_raw_data(scores, taxonomy)

    models = model_columns(scores)
    display_models = [standardize_model_label(col) for col in models]
    rename_map = dict(zip(models, display_models)) if standardize_models else {}

    long_df = scores.melt(
        id_vars=SCORE_ID_COLUMNS,
        value_vars=models,
        var_name="Model",
        value_name="Answer",
    )
    if standardize_models:
        long_df["Model"] = long_df["Model"].map(rename_map)
    long_df["Correct"] = (
        long_df["Answer"].astype(str).str.strip()
        == long_df["RealAnswer"].astype(str).str.strip()
    ).astype(int)
    long_df["Failure"] = 1 - long_df["Correct"]

    tax_clean = taxonomy.rename(columns=TAXONOMY_RENAME)
    merged = pd.merge(long_df, tax_clean, left_on="Number", right_on="Q_No")
    for col in ["Knowledge", "Cognitive", "Complexity", "Risk", "Difficulty", "Task"]:
        merged[col] = clean_category(merged[col])
    return merged
