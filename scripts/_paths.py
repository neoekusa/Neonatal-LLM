from pathlib import Path
import csv
import os


ROOT_DIR = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = ROOT_DIR / "scripts"
OUTPUTS_DIR = ROOT_DIR / "outputs"
DOCS_DIR = ROOT_DIR / "docs"
DATA_DIR = ROOT_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"


def _header(path: Path) -> set[str]:
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as fh:
            return {col.strip() for col in next(csv.reader(fh), [])}
    except (OSError, StopIteration, UnicodeDecodeError):
        return set()


def _discover_csv(env_var: str, preferred_name: str, required_columns: set[str]) -> Path:
    override = os.getenv(env_var)
    if override:
        return Path(override).expanduser()

    preferred = RAW_DATA_DIR / preferred_name
    if preferred.exists():
        return preferred

    matches = [
        path
        for path in sorted(RAW_DATA_DIR.glob("*.csv"))
        if required_columns.issubset(_header(path))
    ]
    if len(matches) == 1:
        return matches[0]
    if matches:
        names = ", ".join(path.name for path in matches)
        raise FileNotFoundError(
            f"Multiple compatible files found in {RAW_DATA_DIR}: {names}. "
            f"Set {env_var} or create {preferred_name} to choose one."
        )
    raise FileNotFoundError(
        f"Could not find {preferred_name} in {RAW_DATA_DIR}, and no CSV had "
        f"the required columns: {', '.join(sorted(required_columns))}."
    )


RAW_SCORES = _discover_csv("NEO_SCORES_CSV", "ydus_llm_scores.csv", {"Number", "RealAnswer"})
RAW_TAXONOMY = _discover_csv(
    "NEO_TAXONOMY_CSV",
    "taxonomy_annotations.csv",
    {"Q No", "Main Domain", "Cognitive Process", "Reasoning  Complexity"},
)
