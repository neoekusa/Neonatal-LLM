# GitHub Upload Checklist

Use this checklist before pushing the repository to GitHub or another public host.

## 1. Check Raw Data

- Confirm whether the raw CSV files may be shared publicly.
- By default, `.gitignore` excludes `data/raw/*.csv`.
- Keep `data/raw/README.md` in the repository even if the raw data are private.

## 2. Keep These Core Repository Components

- `scripts/`
- `README.md`
- `requirements.txt`
- `.gitignore`
- `docs/manuscript/`
- `docs/submission/`
- `docs/notes/` (optional; remove if too internal)

## 3. Keep These Final Main-Manuscript Outputs

- `outputs/Table1_Model_Accuracy.csv`
- `outputs/Table2_Primary_GEE_Reduced_Model.csv`
- `outputs/Table3_Primary_Wald_and_Fit.csv`
- `outputs/TableS2_Consensus_Hard_Questions.csv`
- `outputs/graph_accuracy_rate_by_language_family_dotplot_legend.png`
- `outputs/figure_clinical_domain_and_guideline_distribution.png`
- `outputs/forest_plot_primary_gee_journal.png`
- `outputs/graph_marginal_failure_by_complexity.png`
- `outputs/figure_question_level_incorrect_at_least_1.png`

## 4. Keep These Final Supplementary Outputs

- `outputs/forest_plot_cognitive_complexity_journal.png`
- `outputs/full_exploratory_remember_forest_publication.png`
- `outputs/full_exploratory_collapsed_forest_publication.png`
- `outputs/verified_cramers_v_matrix.png`
- `outputs/verified_vif_values.png`
- `outputs/figure_inter_model_error_correlation_heatmap.png`
- `outputs/figure_cross_model_error_patterns_main_domains.png`

## 5. Optional Final Analytical Tables

Keep these only if you want additional reproducibility material in the public repo:

- `outputs/TableS12_Spearman_Error_Correlation.csv`
- `outputs/TableS13_Top_Spearman_Error_Pairs.csv`
- `outputs/TableS14_Spearman_Error_Correlation_Summary.csv`
- `outputs/TableS1_Expanded_Exploratory_GEE.csv`
- `outputs/TableS9_Marginal_Predicted_Failure_By_Complexity.csv`
- `outputs/marginal_complexity_summary.txt`

## 6. Usually Safe to Leave Ignored

The repository now ignores most legacy, exploratory, debug, and duplicate outputs through `.gitignore`.

## 7. Final Sanity Check

Run:

```bash
git status --short
```

Make sure you do **not** see:

- private raw data you do not want to share
- duplicate output variants
- local scratch files

## 8. Push

```bash
git add .
git commit -m "Organize neonatal benchmark analysis repository"
git push
```
