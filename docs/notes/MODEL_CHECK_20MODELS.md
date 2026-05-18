**20-Model GEE Model Check**

This note summarizes how the four main GEE models were constructed, how they were clustered, and where numerical instability appeared in the 20-model rerun.

**Common Setup**

- Outcome: `Failure` at the question-by-model level
- Unit of analysis: each model response to each question
- Cluster variable: `Number` (question ID)
- Correlation structure: `Exchangeable`
- Family and link: binomial logistic GEE
- Data sources:
  - `data/raw/ydus_llm_scores.csv`
  - `data/raw/taxonomy_annotations.csv`

**Primary Clustered GEE**

- Script source: `scripts/regenerate_primary_submission_outputs.py`
- Formula:
  - `Failure ~ C(Cognitive_Process, Treatment(reference='Remember')) + C(Reasoning_Complexity, Treatment(reference='Low')) + C(Universal_Task_Category, Treatment(reference='1_Physiology_and_Pathophysiology'))`
- Parameter count: `10`
- Robust covariance check:
  - minimum eigenvalue: `0.01299761`
  - negative eigenvalues: `0`
  - `NaN` standard errors: `0`
- Conclusion: stable

**Simplified Clustered GEE**

- Script source: `scripts/run_clean_gee_lpm_analysis.py`
- Formula:
  - `Failure ~ C(Cognitive, Treatment(reference='Remember')) + C(Complexity, Treatment(reference='Low'))`
- Parameter count: `7`
- Robust covariance check:
  - minimum eigenvalue: `0.01505593`
  - negative eigenvalues: `0`
  - `NaN` standard errors: `0`
- Conclusion: stable

**Collapsed Exploratory GEE**

- Script source: `scripts/make_collapsed_exploratory_sensitivity_outputs.py`
- Collapsing rules:
  - `Knowledge_collapsed`: `Metacognitive -> Conceptual`
  - `Cognitive_collapsed`: `Evaluate -> Analyze`
- Formula:
  - `Failure ~ C(Knowledge_collapsed, Treatment(reference='Factual')) + C(Cognitive_collapsed, Treatment(reference='Remember')) + C(Complexity, Treatment(reference='Low')) + C(Risk, Treatment(reference='Low')) + C(Difficulty, Treatment(reference='Low')) + C(Task, Treatment(reference='1_Physiology_and_Pathophysiology'))`
- Parameter count: `16`
- Robust covariance check:
  - minimum eigenvalue: `-9.908295e-15`
  - negative eigenvalues: `0` at the practical threshold used for diagnostics
  - `NaN` standard errors: `0`
- Conclusion: effectively stable and interpretable

**Expanded Exploratory GEE**

- Script source: `scripts/rebuild_full_exploratory_remember.py`
- Formula:
  - `Failure ~ C(Knowledge, Treatment(reference='Factual')) + C(Cognitive, Treatment(reference='Remember')) + C(Complexity, Treatment(reference='Low')) + C(Risk, Treatment(reference='Low')) + C(Difficulty, Treatment(reference='Low')) + C(Task, Treatment(reference='1_Physiology_and_Pathophysiology'))`
- Parameter count: `18`
- Robust covariance check:
  - minimum eigenvalue: `-2.366575`
  - negative eigenvalues: `2`
  - `NaN` standard errors: `2`
  - affected terms:
    - `C(Knowledge, Treatment(reference='Factual'))[T.Metacognitive]`
    - `C(Cognitive, Treatment(reference='Remember'))[T.Evaluate]`
- Conclusion: numerically unstable

**Where the Problem Starts**

- The issue does not originate in clustering itself; all four models use the same question-level clustering and exchangeable correlation.
- The problem begins when the fully expanded exploratory model keeps sparse categories separate instead of collapsing them.
- The two sparsest levels are:
  - `Metacognitive` in knowledge dimension: `5` questions
  - `Evaluate` in cognitive process: `5` questions
- In the expanded model, these sparse levels contribute to an indefinite robust covariance matrix, which then produces unstable joint Wald statistics for `Knowledge` and `Cognitive`.

**Practical Interpretation**

- `Primary clustered GEE`: safe to report
- `Simplified clustered GEE`: safe to report
- `Collapsed exploratory GEE`: safe to report as the interpretable sensitivity analysis
- `Expanded exploratory GEE`:
  - coefficient table can be shown with caution
  - robust joint Wald tests for `Knowledge` and `Cognitive` should not be interpreted directly
  - if a sensitivity value is needed, a model-based covariance Wald calculation is more stable, but it should be labeled as secondary
