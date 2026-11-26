"""Release layout and input overrides for the v4 analysis."""
import os
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
OUTPUTS_DIR = ROOT_DIR / "outputs" / "v4"
RAW_DATA_DIR = ROOT_DIR / "data" / "raw"
SCORE_SOURCE = RAW_DATA_DIR / "ydus_llm_scores.csv"
TAXONOMY_SOURCE = RAW_DATA_DIR / "taxonomy_annotations.csv"


def _input_path(env, default):
    path = Path(os.getenv(env) or default).expanduser().resolve()
    if not path.is_relative_to(ROOT_DIR):
        raise ValueError(f"{env} must point to a file in the repository: {path}")
    if not path.is_file():
        raise FileNotFoundError(f"Missing analysis input: {path}")
    return path


def raw_paths():
    return _input_path("NEO_SCORES_CSV", SCORE_SOURCE), _input_path("NEO_TAXONOMY_CSV", TAXONOMY_SOURCE)
