**Joint Wald Tests Across GEE Specifications (20 models)**

**Manuscript-ready summary**

| Model | Variable | Wald χ² | df | p-value |
|---|---|---:|---:|---:|
| Primary clustered GEE | Cognitive process | 6.19 | 4 | 0.185 |
| Primary clustered GEE | Reasoning complexity | 12.60 | 2 | 0.002 |
| Primary clustered GEE | Universal task category | 0.61 | 3 | 0.893 |
| Simplified clustered GEE | Cognitive process | 8.74 | 4 | 0.068 |
| Simplified clustered GEE | Reasoning complexity | 13.17 | 2 | 0.001 |
| Collapsed exploratory GEE | Knowledge dimension (collapsed) | 0.39 | 2 | 0.821 |
| Collapsed exploratory GEE | Cognitive process (collapsed) | 5.06 | 3 | 0.167 |
| Collapsed exploratory GEE | Reasoning complexity | 10.45 | 2 | 0.005 |
| Collapsed exploratory GEE | Clinical risk | 0.62 | 4 | 0.960 |
| Collapsed exploratory GEE | Difficulty | 0.41 | 2 | 0.814 |
| Collapsed exploratory GEE | Universal task category | 0.50 | 3 | 0.919 |
| Expanded exploratory GEE | Knowledge dimension | Unstable | 3 | Unstable |
| Expanded exploratory GEE | Cognitive process | Unstable | 4 | Unstable |
| Expanded exploratory GEE | Reasoning complexity | 10.47 | 2 | 0.005 |
| Expanded exploratory GEE | Clinical risk | 0.56 | 3 | 0.905 |
| Expanded exploratory GEE | Difficulty | 0.39 | 2 | 0.821 |
| Expanded exploratory GEE | Universal task category | 0.43 | 3 | 0.934 |

**Supplement-ready expanded-model sensitivity**

| Model | Variable | Wald χ² | df | p-value | Notes |
|---|---|---:|---:|---:|---|
| Expanded exploratory GEE (raw robust) | Knowledge dimension | -0.16 | 3 | 1.000 | Noninterpretable because robust covariance matrix was indefinite |
| Expanded exploratory GEE (raw robust) | Cognitive process | -10.43 | 4 | 1.000 | Noninterpretable because robust covariance matrix was indefinite |
| Expanded exploratory GEE (raw robust) | Reasoning complexity | 10.47 | 2 | 0.005 | Stable positive signal |
| Expanded exploratory GEE (raw robust) | Clinical risk | 0.56 | 3 | 0.905 | Stable null |
| Expanded exploratory GEE (raw robust) | Difficulty | 0.39 | 2 | 0.821 | Stable null |
| Expanded exploratory GEE (raw robust) | Universal task category | 0.43 | 3 | 0.934 | Stable null |
| Expanded exploratory GEE (model-based covariance sensitivity) | Knowledge dimension | 0.01 | 3 | 1.000 | Stable sensitivity result |
| Expanded exploratory GEE (model-based covariance sensitivity) | Cognitive process | 0.22 | 4 | 0.994 | Stable sensitivity result |
| Expanded exploratory GEE (model-based covariance sensitivity) | Reasoning complexity | 8.19 | 2 | 0.017 | Stable sensitivity result |
| Expanded exploratory GEE (model-based covariance sensitivity) | Clinical risk | 0.66 | 3 | 0.883 | Stable sensitivity result |
| Expanded exploratory GEE (model-based covariance sensitivity) | Difficulty | 0.26 | 2 | 0.880 | Stable sensitivity result |
| Expanded exploratory GEE (model-based covariance sensitivity) | Universal task category | 0.97 | 3 | 0.809 | Stable sensitivity result |

**Why negative Wald values appeared**

Wald chi-square statistics should not be negative in a well-behaved model. The negative values in the fully expanded exploratory GEE arose because the robust covariance matrix became numerically indefinite. In the 20-model rerun, the minimum eigenvalue of the robust covariance matrix was `-2.37`, there were `2` negative eigenvalues, and `2` sparse-category coefficients had undefined standard errors:

- `Knowledge dimension: Metacognitive vs Factual`
- `Cognitive process: Evaluate vs Remember`

These sparse levels each corresponded to only `5` questions. Once all overlapping taxonomy domains were included simultaneously, the robust term-level Wald calculation for `Knowledge` and `Cognitive` no longer behaved as a valid positive quadratic form. This is why the raw robust expanded-model output produced impossible negative Wald statistics instead of interpretable inferential results.

**Practical interpretation**

- The negative expanded-model Wald values do not indicate a protective or inverse domain effect.
- They indicate that the raw robust joint Wald calculation was not numerically valid for those domains.
- The interpretable inference comes from the stable primary, simplified, and collapsed models, supported by the model-based expanded sensitivity analysis.
