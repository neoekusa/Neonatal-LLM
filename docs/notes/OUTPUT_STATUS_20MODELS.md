# Output Status for 20-Model Update

This note documents which files in `outputs/` are confirmed to reflect the 20-model May 2026 rerun, which files are likely older 18-model or legacy outputs, and which result families can be reproduced from the retained scripts and input files.

## Confirmed 20-Model Outputs

These files were regenerated after switching the score source to:

- `/Users/bagcilab/Downloads/YDUS_LLM_KEYS_all_LLMS _EK_v5_may_son.csv`

and can be treated as the current final 20-model outputs.

### Main manuscript tables

- `Table1_Model_Accuracy.csv`
- `Table2_Primary_GEE_Reduced_Model.csv`
- `Table3_Primary_Wald_and_Fit.csv`
- `TableS2_Consensus_Hard_Questions.csv`

### Supplementary and analytical tables

- `TableS1_Expanded_Exploratory_GEE.csv`
- `TableS4_QIC_QICu_Model_Comparison.csv`
- `TableS4_QIC_QICu_Model_Comparison_Annotated.csv`
- `TableS5_Reference_Coding_QIC_Check.csv`
- `TableS6_Joint_Wald_Comparison.csv`
- `TableS6_Collapsed_Exploratory_Wald.csv`
- `TableS9_Marginal_Predicted_Failure_By_Complexity.csv`
- `TableS11_Cochrans_Q_All_Models.csv`
- `TableS12_Spearman_Error_Correlation.csv`
- `TableS13_Top_Spearman_Error_Pairs.csv`
- `TableS14_Spearman_Error_Correlation_Summary.csv`

### Main manuscript figures

- `graph_accuracy_rate_by_language_family_dotplot_legend.png`
- `figure_clinical_domain_and_guideline_distribution.png`
- `forest_plot_primary_gee_journal.png`
- `graph_marginal_failure_by_complexity.png`
- `figure_question_level_incorrect_at_least_1.png`

### Supplementary figures

- `forest_plot_cognitive_complexity_journal.png`
- `full_exploratory_remember_forest_publication.png`
- `full_exploratory_collapsed_forest_publication.png`
- `verified_cramers_v_matrix.png`
- `verified_vif_values.png`
- `figure_inter_model_error_correlation_heatmap.png`
- `figure_cross_model_error_patterns_main_domains.png`

### Additional updated question-level figures

- `figure_question_level_correctness_matrix.png`
- `figure_question_level_incorrect_at_least_10.png`

### Supporting regenerated CSV and summary files

- `model_accuracy_report.csv`
- `gee_model_error_rates.csv`
- `high_journal_primary_gee_coefficients.csv`
- `high_journal_primary_gee_wald.csv`
- `high_journal_primary_qic_qicu.csv`
- `high_journal_primary_summary.csv`
- `clean_gee_results.csv`
- `clean_gee_qic_qicu.csv`
- `clean_lpm_results.csv`
- `clean_gee_lpm_vif.csv`
- `clean_gee_lpm_summary.txt`
- `full_exploratory_remember_results.csv`
- `full_exploratory_remember_qic_qicu.csv`
- `full_exploratory_remember_joint_wald.csv`
- `exploratory_collapsed_meta_eval_results.csv`
- `exploratory_collapsed_meta_eval_wald.csv`
- `collapsed_exploratory_qic_qicu.csv`
- `all_model_qic_qicu_comparison.csv`
- `all_model_qic_qicu_comparison_summary.txt`
- `full_model_reference_qic_check.csv`
- `marginal_complexity_summary.txt`
- `clinical_domain_distribution.csv`
- `guideline_source_family_distribution.csv`
- `cross_model_error_by_main_domain.csv`
- `question_level_correctness_matrix.csv`
- `question_level_incorrect_at_least_1.csv`
- `question_level_incorrect_at_least_10.csv`
- `clean_gee_joint_wald.csv`
- `comparison_previous_vs_cognitive_complexity_model.csv`
- `comparison_previous_vs_cognitive_complexity_summary.txt`
- `verified_cramers_v_matrix.csv`
- `verified_vif_values.csv`

## Likely Older 18-Model or Legacy Outputs

These files were not refreshed during the 20-model rerun, or they belong to older exploratory / reviewer-only workstreams. They should not be used as current final outputs without rerunning them explicitly.

### Older sensitivity / multiplicity tables

- `TableS15_GEE_Correlation_Structure_Sensitivity.csv`
- `TableS15b_GEE_Correlation_Structure_Complexity_Coefficients.csv`
- `TableS16_Cognitive_Process_Multiple_Comparisons.csv`
- `TableS15_Cognitive_Process_Multiple_Comparison_Adjustment.csv`
- `TableS16_Primary_GEE_Robust_SE.csv`
- `TableS17_Marginal_Predicted_Failure_With_CI.csv`
- `gee_correlation_structure_sensitivity.csv`
- `gee_correlation_structure_complexity_coefficients.csv`

### Older package exports

- `Neonatology_Submission_Package.md`
- `Neonatology_Submission_Inventory.csv`

### Older publication / alternate plot variants

- `TableS6_Joint_Wald_Comparison_Publication.csv`
- `forest_plot_primary_gee.png`
- `forest_plot_primary_gee_labeled.png`
- `gee_factual_apply_reference_forest.png`
- `gee_factual_apply_reference_forest_labeled.png`
- `figure_cross_model_error_patterns_main_domains_rocket.png`
- `figure_cross_model_error_patterns_main_domains_viridis.png`
- `figure_cross_model_error_patterns_main_domains_ylorrd.png`
- `graph_qic_qicu_primary_vs_expanded.png`
- `graph_joint_wald_primary_vs_expanded.png`
- `graph_complexity_primary_vs_expanded.png`
- `graph_llm_family_accuracy_dotplot.png`
- `graph_llm_family_clustering.png`
- `graph_accuracy_rate_by_language_family_dotplot.png`
- `graph_lpm_primary_model.png`

### Legacy exploratory / debug / discarded analysis outputs

- `doublecheck_*`
- `no_model_*`
- `no_difficulty_*`
- `no_clinicalrisk_*`
- `glmm_*`
- `reduced_glmm_*`
- `collinearity_*`
- `gee_question_cluster_*`
- `gee_qic_qicu_model_comparison*.csv`
- `taxonomy_hardest_categories*.csv`
- `model_taxonomy_failure_breakdown.csv`
- `gee_epp_notes.txt`
- `gee_events_per_parameter_sensitivity_summary.csv`
- `TableS15_GEE_EPP_and_Clusters.csv`
- `model_spec_search_for_screenshot.csv`

## Reproducible Output Families

Even when an older output has been overwritten, the results can still be regenerated as long as the corresponding input file is available.

### Current 20-model input

- `/Users/bagcilab/Downloads/YDUS_LLM_KEYS_all_LLMS _EK_v5_may_son.csv`

### Previous 18-model input

- `/Users/bagcilab/Downloads/YDUS_LLM_KEYS_all_LLMS _EK_v5_april_son.csv`

### Core scripts used for regeneration

- `scripts/regenerate_primary_submission_outputs.py`
- `scripts/run_clean_gee_lpm_analysis.py`
- `scripts/rebuild_full_exploratory_remember.py`
- `scripts/make_collapsed_exploratory_sensitivity_outputs.py`
- `scripts/make_joint_wald_comparison_table.py`
- `scripts/compare_all_model_qic.py`
- `scripts/make_marginal_complexity_outputs.py`
- `scripts/make_consensus_hard_table.py`
- `scripts/make_spearman_error_heatmap.py`
- `scripts/make_verified_collinearity_figures.py`
- `scripts/make_clinical_domain_guideline_figures.py`
- `scripts/update_family_accuracy_dotplot_with_legend.py`
- `scripts/make_cognitive_complexity_comparison.py`

## Practical Rule

- Files with May 14 timestamps from the 20:35 to 20:45 rerun window can generally be treated as 20-model outputs.
- Files last updated on May 7, April 28, or April 24 should be treated as older or mixed unless explicitly rerun.
- If needed, the 18-model final outputs can be regenerated by pointing `data/raw/ydus_llm_scores.csv` back to the April input file and rerunning the same scripts.
