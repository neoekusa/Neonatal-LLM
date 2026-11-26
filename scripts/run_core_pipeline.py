"""Rebuild the v4 release from its two source CSVs."""
import argparse
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import sys
import platform
import shutil
import subprocess
from tempfile import TemporaryDirectory

from _paths import OUTPUTS_DIR, ROOT_DIR, raw_paths
from analysis_data import load_long_analysis_df
import descriptive_v4
import figures_v4
import inference_v4
from release_output import staged_outputs


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--with-figures", action="store_true", help="Also regenerate the four manuscript figures.")
    parser.add_argument("--python-only", action="store_true",
                        help="Explicitly omit the crossed R/lme4 fit from this generation.")
    args = parser.parse_args()
    executable = "Rscript.exe" if os.name == "nt" else "Rscript"
    local_r = Path(sys.executable).parent / executable
    default_r = str(local_r) if local_r.is_file() else executable
    rscript = shutil.which(os.getenv("NEO_RSCRIPT", default_r))
    if not args.python_only and not rscript:
        parser.exit(2, "The full v4 analysis requires Rscript and lme4. Install R and lme4, set NEO_RSCRIPT "
                       "to an Rscript executable, or request --python-only.\n")
    scores, taxonomy = raw_paths()
    df = load_long_analysis_df(scores, taxonomy)
    print(f"{df.Number.nunique()} questions × {df.Model.nunique()} recorded columns. "
          f"{df.Failure.sum()} incorrect responses of {len(df)}.", flush=True)
    with staged_outputs() as out:
        descriptive_v4.run(df, out)
        inference_v4.run(df, out)
        if not args.python_only:
            with TemporaryDirectory() as tmp:
                panel = Path(tmp) / "panel.csv"
                df[["Number", "Model", "Failure", "Complexity", "Cognitive", "Task"]].to_csv(panel, index=False)
                script = Path(__file__).with_name("crossed_random_effects.R").resolve()
                subprocess.run([rscript, str(script), str(panel), str(out)], check=True)
        if args.with_figures:
            figures_v4.run(out)
        inputs = {"scores": scores, "taxonomy": taxonomy}
        manifest = {
            "version": "v4", "python_version": platform.python_version(),
            "packages": {p: importlib.metadata.version(p) for p in
                         ("pandas", "numpy", "statsmodels", "scipy", "patsy", "matplotlib", "Pillow", "filelock")},
            "input_files": {key: p.relative_to(ROOT_DIR).as_posix() for key, p in inputs.items()},
            "inputs_sha256": {key: hashlib.sha256(p.read_bytes()).hexdigest() for key, p in inputs.items()},
            "questions": int(df.Number.nunique()), "recorded_columns": int(df.Model.nunique()),
            "responses": len(df), "incorrect": int(df.Failure.sum()),
            "crossed_model": "omitted by --python-only" if args.python_only else "fitted",
        }
        (out / "run_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote v4 results to {OUTPUTS_DIR}")


if __name__ == "__main__":
    main()
