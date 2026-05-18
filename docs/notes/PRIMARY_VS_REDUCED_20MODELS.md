# Primary vs Reduced Model Comparison (20 Models)

This file provides a clean comparison between the current primary clustered GEE model and the reduced clustered GEE model after updating the benchmark to 20 evaluated language models.

## Model Definitions

### Primary clustered GEE model

- Predictors:
  - Cognitive process
  - Reasoning complexity
  - Universal task category
- Interpretation:
  - This is the main inferential model used in the manuscript.
  - It asks whether error is explained by cognitive process, reasoning complexity, and broad task category after clustering responses by question.

### Reduced clustered GEE model

- Predictors:
  - Cognitive process
  - Reasoning complexity
- Interpretation:
  - This is the simplified supportive model.
  - It asks whether the main signal persists after removing universal task category.

## 20-Model Results Summary

| Comparison Item | Primary Model | Reduced Model |
|---|---:|---:|
| Model specification | Cognitive + Complexity + Universal Task | Cognitive + Complexity |
| Reasoning complexity joint Wald | chi-square=12.60, p=0.0018 | chi-square=13.17, p=0.0014 |
| Cognitive process joint Wald | chi-square=6.19, p=0.185 | chi-square=8.74, p=0.068 |
| Moderate vs Low complexity | OR=5.46 [2.12, 14.08], p<0.001 | OR=5.14 [2.11, 12.54], p<0.001 |
| High vs Low complexity | OR=7.59 [1.77, 32.55], p=0.006 | OR=6.54 [1.57, 27.25], p=0.010 |
| Apply vs Remember | OR=0.21 [0.05, 0.86], p=0.030 | OR=0.20 [0.06, 0.69], p=0.011 |
| QIC | 1943.66 | 1943.74 |
| QICu | 1943.65 | 1944.98 |

## Interpretation

### What stayed the same

- Reasoning complexity remained the most stable predictor of failure in both models.
- Moderate-complexity and high-complexity items were associated with substantially higher odds of failure than low-complexity items in both specifications.
- The magnitude of the complexity effect was very similar across the two models.

### What changed

- Universal task category was included in the primary model but removed from the reduced model.
- Removing universal task category did not materially change the reasoning-complexity signal.
- Cognitive process remained non-significant at the domain level in both models, although the reduced model showed a somewhat stronger borderline signal.

### Model-selection implication

- The primary model remains preferable for main inference because it preserves the planned taxonomy structure while still showing stable fit.
- The reduced model serves as a supportive robustness analysis showing that the main result does not depend on inclusion of universal task category.
- The near-identical QIC values suggest that dropping universal task category does not improve fit enough to change the main inferential choice.

## Key Takeaway

The 20-model rerun does not change the main statistical conclusion: reasoning complexity remains the dominant and reproducible determinant of LLM failure, whereas cognitive process is not independently robust at the domain level and universal task category contributes little explanatory value.

## Paste-Ready Results Sentence

In the 20-model analysis, reasoning complexity remained the most consistent predictor of failure across both the primary clustered GEE model and the reduced clustered GEE model. In the primary model, reasoning complexity was independently associated with error (Wald chi-square=12.60, df=2, p=0.0018), whereas cognitive process (Wald chi-square=6.19, df=4, p=0.185) and universal task category (Wald chi-square=0.61, df=3, p=0.893) were not. A supportive reduced model including only cognitive process and reasoning complexity yielded similar effect sizes and nearly identical model fit, confirming that the main signal was driven by reasoning complexity rather than by broad task labeling.

## Paste-Ready Discussion Sentence

Comparison of the primary and reduced clustered GEE models showed that removing universal task category did not materially change the association between reasoning complexity and failure. This supports the interpretation that the central vulnerability in the 20-model benchmark lies in integrative reasoning burden rather than in broad task classification.

## Source Files

- `outputs/Table2_Primary_GEE_Reduced_Model.csv`
- `outputs/Table3_Primary_Wald_and_Fit.csv`
- `outputs/clean_gee_results.csv`
- `outputs/clean_gee_qic_qicu.csv`
- `outputs/clean_gee_joint_wald.csv`
- `outputs/comparison_previous_vs_cognitive_complexity_model.csv`
