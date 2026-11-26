"""Rebuild the v4 manuscript figures from an existing run's result tables."""
from _paths import OUTPUTS_DIR
from figures_v4 import run
from release_output import staged_outputs


if __name__ == "__main__":
    with staged_outputs(existing=True) as out:
        run(out)
    print(f"Wrote four manuscript figures to {OUTPUTS_DIR}")
