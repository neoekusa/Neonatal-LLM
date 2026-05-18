# Neonatology LLM Benchmark Analysis

This repository contains the analysis code, generated outputs, and manuscript support files for a neonatal subspecialty benchmarking study of large language models (LLMs).

## Repository Structure

```text
.
├── data/
│   └── raw/                # input CSV files (or symlinks to local copies)
├── docs/
│   ├── manuscript/         # manuscript drafts and legend notes
│   ├── notes/              # working notes and revision memos
│   └── submission/         # submission package inventories
├── outputs/                # generated tables, figures, and summary files
├── scripts/                # analysis and figure-generation scripts
└── main.py                 # minimal GUI launcher
```

## Input Data

The scripts first look for the following stable file names:

- `data/raw/ydus_llm_scores.csv`
- `data/raw/taxonomy_annotations.csv`

If those files are not present, the path helper scans `data/raw/*.csv` and selects
the unique CSV matching the expected score or taxonomy schema. You can still set:

- `NEO_SCORES_CSV`
- `NEO_TAXONOMY_CSV`

to override discovery explicitly.

The raw files do not need a persistent processed copy. The scripts perform the
required processing in memory: trim headers/answers, reshape scores from wide to
long format, compute correctness/failure, merge taxonomy labels, and normalize
categorical labels for statistical formulas.

## Python Environment

Create a virtual environment and install dependencies with the platform setup script:

```bash
./setup_linux.sh
# or
./setup_macos.sh
```

Then launch the graphical runner:

```bash
.venv/bin/python main.py
```

The GUI provides three actions: `Run` for the full core-plus-figure workflow,
`Run Core Only` for statistical tables/models, and `Run Figure Only` for plots
and the submission package. It also includes a live console and PNG figure viewer.

The GUI uses Tk, which must be available in the Python build. The setup scripts
check this and print platform-specific guidance if Tk is missing.

Manual setup is also possible:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

## Core Analysis Workflow

For a reproducible run, use the orchestration scripts:

```bash
PYTHONPATH=scripts python scripts/run_core_pipeline.py
PYTHONPATH=scripts python scripts/run_figure_pipeline.py
```

The distributed scripts remain importable and runnable individually. The pipeline
scripts only call them in dependency order.

The main analysis can be reproduced with the following scripts:

1. `scripts/run_clean_gee_lpm_analysis.py`
   - fits the reduced clustered GEE model
   - fits the clustered linear probability model
   - writes reduced-model coefficients and fit summaries

2. `scripts/rebuild_full_exploratory_remember.py`
   - fits the expanded exploratory clustered GEE model
   - produces exploratory coefficient tables and forest plots

3. `scripts/make_collapsed_exploratory_sensitivity_outputs.py`
   - runs the sparse-category sensitivity analysis
   - merges `Metacognitive -> Conceptual` and `Evaluate -> Analyze`

4. `scripts/make_joint_wald_comparison_table.py`
   - generates joint Wald comparison outputs

5. `scripts/compare_all_model_qic.py`
   - compares candidate clustered GEE specifications using QIC/QICu

6. `scripts/make_marginal_complexity_outputs.py`
   - fits the primary clustered GEE model and regenerates Figure 4 / Table S9
   - computes average marginal predicted failure probabilities by setting reasoning complexity
     to each level across all observations while preserving the observed distribution of the
     remaining covariates
   - writes `outputs/TableS9_Marginal_Predicted_Failure_By_Complexity.csv`,
     `outputs/graph_marginal_failure_by_complexity.png`, and
     `outputs/marginal_complexity_summary.txt`

7. `scripts/make_verified_collinearity_figures.py`
   - produces Cramer's V and VIF diagnostics

8. `scripts/make_clinical_domain_guideline_figures.py`
   - builds clinical-domain, guideline-source, and question-level error figures

9. `scripts/make_spearman_error_heatmap.py`
   - builds the inter-model Spearman error-correlation heatmap

10. `scripts/update_family_accuracy_dotplot_with_legend.py`
    - regenerates the family-level accuracy dot plot with legend

## Notable Outputs

Key manuscript-ready files are written to `outputs/`, including:

- `Table1_Model_Accuracy.csv`
- `Table2_Primary_GEE_Reduced_Model.csv`
- `Table3_Primary_Wald_and_Fit.csv`
- `TableS2_Consensus_Hard_Questions.csv`
- `forest_plot_primary_gee_journal.png`
- `graph_marginal_failure_by_complexity.png`
- `figure_clinical_domain_and_guideline_distribution.png`
- `figure_question_level_incorrect_at_least_1.png`

## Notes

- Scripts were originally developed interactively and now share a common path helper in `scripts/_paths.py`.
- Most outputs are regenerated in place under `outputs/`.
- Manuscript and submission support materials are preserved under `docs/`.
- The manuscript values for marginal failure by reasoning complexity (`4.8%`, `20.8%`, and `26.3%`)
  are reproducible from the primary clustered GEE using `scripts/make_marginal_complexity_outputs.py`.
