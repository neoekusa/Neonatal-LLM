"""Publish a complete set of generated outputs after a successful run."""
from contextlib import contextmanager
from pathlib import Path
import shutil
from tempfile import TemporaryDirectory

from filelock import FileLock

from _paths import OUTPUTS_DIR


@contextmanager
def staged_outputs(*, existing=False):
    parent = OUTPUTS_DIR.parent
    parent.mkdir(parents=True, exist_ok=True)
    with FileLock(str(parent / ".v4.lock")), TemporaryDirectory(dir=parent) as tmp:
        stage = Path(tmp) / "next"
        if existing:
            if not OUTPUTS_DIR.is_dir():
                raise FileNotFoundError("Generate v4 tables with run_core_pipeline.py first.")
            shutil.copytree(OUTPUTS_DIR, stage)
        else:
            stage.mkdir()
        yield stage
        previous = Path(tmp) / "previous"
        if OUTPUTS_DIR.exists():
            OUTPUTS_DIR.rename(previous)
        try:
            stage.rename(OUTPUTS_DIR)
        except OSError:
            if previous.exists():
                previous.rename(OUTPUTS_DIR)
            raise
