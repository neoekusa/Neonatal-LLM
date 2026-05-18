# Neonatology Submission Package

## Main Manuscript Figures

- Figure 1: `forest_plot_primary_gee_journal.png`
  Purpose: Primary clustered GEE forest plot
  Legend: Forest plot of adjusted odds ratios for failure from the primary question-clustered GEE model. Reference categories were Remember for cognitive process, Low for reasoning complexity, and Physiology and Pathophysiology for universal task category. Error bars indicate 95% confidence intervals.

- Figure 2: `graph_marginal_failure_by_complexity.png`
  Purpose: Marginal predicted failure risk by reasoning complexity
  Legend: Model-based marginal predicted probability of failure from the primary question-clustered GEE model across reasoning-complexity strata.

## Supplementary Figures

- Supplementary Figure 1: `forest_plot_cognitive_complexity_journal.png`
  Purpose: Supportive clustered GEE with cognitive process and complexity only
  Legend: Forest plot of the supportive simplified clustered GEE model including only cognitive process and reasoning complexity.

- Supplementary Figure 2: `full_exploratory_remember_forest.png`
  Purpose: Expanded exploratory full-taxonomy GEE forest plot
  Legend: Forest plot from the expanded exploratory clustered GEE model including knowledge dimension, cognitive process, reasoning complexity, clinical risk, difficulty, and universal task category.

- Supplementary Figure 3: `full_exploratory_collapsed_forest_publication.png`
  Purpose: Collapsed sparse-category exploratory sensitivity forest plot
  Legend: Sensitivity forest plot after collapsing sparse metacognitive and evaluate categories into adjacent taxonomy groups.

- Supplementary Figure 4: `verified_cramers_v_matrix.png`
  Purpose: Verified categorical collinearity matrix
  Legend: Verified Cramer's V matrix showing the degree of association among taxonomy predictors.

- Supplementary Figure 5: `verified_vif_values.png`
  Purpose: Verified VIF plot
  Legend: Verified variance inflation factor values for taxonomy predictors used to assess multicollinearity.

- Supplementary Figure 6: `figure_inter_model_error_correlation_heatmap.png`
  Purpose: Inter-model error correlation heatmap
  Legend: Spearman correlation heatmap comparing model-level error patterns across questions.

- Supplementary Figure 7: `figure_cross_model_error_patterns_main_domains.png`
  Purpose: Cross-model error patterns across main clinical domains
  Legend: Heatmap of model-specific error rates across main clinical domains, with models grouped by family.

## Main Manuscript Tables

- Table 1: `Table1_Model_Accuracy.csv`
  Purpose: Model accuracy summary
  Legend: Overall accuracy of each language model across the full neonatal question set.

- Table 2: `Table2_Primary_GEE_Reduced_Model.csv`
  Purpose: Primary clustered GEE coefficient table
  Legend: Primary question-clustered GEE model examining associations between taxonomy features and model failure.

- Table 3: `Table3_Primary_Wald_and_Fit.csv`
  Purpose: Joint Wald tests and fit statistics for primary model
  Legend: Joint Wald chi-square tests and model-fit statistics for the primary reduced clustered GEE model.

## Supplementary Tables

- Supplementary Table 1: `TableS1_Expanded_Exploratory_GEE.csv`
  Purpose: Expanded exploratory GEE results
  Legend: Expanded exploratory clustered GEE model including knowledge dimension, cognitive process, reasoning complexity, clinical risk, difficulty, and universal task category.

- Supplementary Table 2: `TableS2_Consensus_Hard_Questions.csv`
  Purpose: Consensus hard questions
  Legend: Questions missed by at least five models, with taxonomy annotations.

- Supplementary Table 3: `comparison_previous_vs_cognitive_complexity_model.csv`
  Purpose: Primary versus simplified model comparison
  Legend: Comparison of the primary clustered GEE model and the simplified cognitive process plus reasoning complexity model.

- Supplementary Table 4: `all_model_qic_qicu_comparison.csv`
  Purpose: QIC/QICu comparison across all candidate models
  Legend: QIC and QICu comparison across all candidate clustered GEE model specifications.

- Supplementary Table 5: `full_model_reference_qic_check.csv`
  Purpose: Reference-category QIC diagnostic
  Legend: Reference-coding diagnostic for the expanded full-taxonomy model. QIC and QICu are reported as positive model-fit criteria. The diagnostic also includes quasi-likelihood, explicitly labeled as not QIC, because it can be negative. Recoded fits are not treated as separate model-ranking entries.

- Supplementary Table 6: `clean_gee_lpm_vif.csv`
  Purpose: VIF for simplified cognitive-complexity model
  Legend: Variance inflation factor values for dummy-coded terms in the simplified cognitive process plus reasoning complexity model.

- Supplementary Table 7: `verified_cramers_v_matrix.csv`
  Purpose: Verified Cramer's V source matrix
  Legend: Source Cramer's V matrix underlying the categorical collinearity heatmap.

- Supplementary Table 8: `verified_vif_values.csv`
  Purpose: Verified VIF source table
  Legend: Source variance inflation factor values underlying the verified VIF plot.

## Statistical Narrative

Primary inference is based on the reduced question-clustered GEE model including cognitive process, reasoning complexity, and universal task category. The main finding is that reasoning complexity is the most robust predictor of failure. Expanded taxonomy models are retained as supplementary exploratory analyses because they show poorer fit and unstable coefficients.
