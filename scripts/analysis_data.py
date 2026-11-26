"""Load the recorded score sheet and one consensus taxonomy row per question."""
import csv
from pathlib import Path

import pandas as pd

from _model_labels import standardize_model_label
from _paths import raw_paths


SCORE_IDS = ["Number", "RealAnswer"]
TAXONOMY = {
    "Q No": "Number", "Main Domain": "Main Domain", "Subdomain": "Subdomain",
    "Knowledge Dimension": "Knowledge", "Cognitive Process": "Cognitive",
    "Reasoning Complexity": "Complexity", "Clinical Risk": "Risk", "Difficulty": "Difficulty",
    "Main Guideline": "Main Guideline", "Universal Task Category": "Task",
}
OPTIONS = set("ABCDE")
NON_SINGLE = {"NR", "Selected all"}


def read_table(path: Path) -> pd.DataFrame:
    # Read the header before pandas can silently disambiguate repeated column names.
    with path.open(encoding="utf-8-sig", newline="") as source:
        reader = csv.reader(source, strict=True)
        header = [" ".join(value.split()) for value in next(reader, [])]
        if not header or len(set(header)) != len(header) or "" in header:
            raise ValueError(f"{path.name} has an empty or repeated column name")
        records = []
        for line, row in enumerate(reader, 2):
            if len(row) != len(header):
                raise ValueError(f"{path.name} row {line} has {len(row)} fields, expected {len(header)}")
            records.append([value.strip() for value in row])
    return pd.DataFrame(records, columns=header)


def question_ids(values: pd.Series, source: str) -> pd.Series:
    values = pd.to_numeric(values, errors="raise")
    if values.empty or values.isna().any() or (values <= 0).any() or (values % 1 != 0).any():
        raise ValueError(f"{source} requires positive integer question numbers")
    if values.duplicated().any():
        raise ValueError(f"{source} repeats question numbers {values[values.duplicated()].tolist()}")
    return values.astype(int)


def load_long_analysis_df(scores_path=None, taxonomy_path=None):
    if scores_path is None or taxonomy_path is None:
        default_scores, default_taxonomy = raw_paths()
        scores_path = default_scores if scores_path is None else scores_path
        taxonomy_path = default_taxonomy if taxonomy_path is None else taxonomy_path
    scores, taxonomy = read_table(Path(scores_path)), read_table(Path(taxonomy_path))
    for table, required in [(scores, SCORE_IDS), (taxonomy, TAXONOMY)]:
        missing = set(required) - set(table)
        if missing:
            raise ValueError(f"Missing required columns: {sorted(missing)}")
    taxonomy = taxonomy[list(TAXONOMY)].rename(columns=TAXONOMY)
    scores["Number"] = question_ids(scores["Number"], "Scores")
    taxonomy["Number"] = question_ids(taxonomy["Number"], "Taxonomy")
    if set(scores.Number) != set(taxonomy.Number):
        raise ValueError("Question numbers differ between the score sheet and taxonomy")
    if (taxonomy == "").any().any() or not scores.RealAnswer.isin(OPTIONS).all():
        raise ValueError("Check for blank taxonomy fields or keys outside A–E")

    models = scores.columns.difference(SCORE_IDS, sort=False)
    labels = [standardize_model_label(m) for m in models]
    if len(labels) < 2 or len(set(labels)) != len(labels):
        raise ValueError("Paired analysis requires distinct model columns after label normalization")
    long = scores.rename(columns=dict(zip(models, labels))).melt(
        id_vars=SCORE_IDS, var_name="Model", value_name="Answer")
    invalid = ~long.Answer.isin(OPTIONS | NON_SINGLE)
    if invalid.any():
        raise ValueError(f"Unrecognized or missing responses:\n{long.loc[invalid].head().to_string(index=False)}")
    long["Correct"] = long.Answer.eq(long.RealAnswer).astype(int)
    long["Failure"] = 1 - long.Correct
    # Preserve original clinical labels. The task code retains the study's reference coding.
    taxonomy["Task"] = (taxonomy.Task.str.replace(r"\s+", "_", regex=True)
                        .str.replace(".", "", regex=False).str.replace("/", "_", regex=False))
    return long.merge(taxonomy, on="Number", validate="many_to_one").sort_values(
        ["Number", "Model"], ignore_index=True)
