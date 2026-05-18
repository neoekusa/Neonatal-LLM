**Neonatology Revision Memo**

**What Needs To Change**

The current draft and supplementary documents contain several statistical statements that are no longer aligned with the final clustered analyses. The main issues are:

- The abstract currently states `N=2,286 independent observations`. This should be avoided because the repeated model responses are not independent. The wording should instead emphasize clustered observations at the question level.
- The abstract currently reports `Reasoning Complexity` as significant at `p < 0.001` with `aOR 9.63` and `95% CI 2.84-32.62`. Those numbers come from an exploratory expanded model and should not be presented as the main result.
- The abstract currently reports large LPM drops for `Apply` and `Analyze`. These are not supported by the final clustered primary analysis and should not be highlighted as core conclusions.
- The current supplementary file includes outdated `QIC`, `Wald chi-square`, `EPP`, and sensitivity-analysis numbers that do not match the final model set we validated.
- Some documents appear to use non-clustered logistic outputs or older exploratory model outputs as if they were the primary inference. For submission, the primary inferential model must remain the reduced question-clustered GEE.

**Primary Statistical Story To Keep**

Primary inferential model:

`Failure ~ Cognitive Process + Reasoning Complexity + Universal Task Category`

with:

- clustered GEE
- binomial family
- logit link
- exchangeable working correlation
- question as the clustering unit

Primary result:

- `Reasoning Complexity` was the only robust independent predictor of failure
- `Moderate vs Low`: aOR `5.76`, 95% CI `2.14-15.48`, `p<0.001`
- `High vs Low`: aOR `8.10`, 95% CI `1.82-36.11`, `p=0.006`
- joint Wald chi-square for `Reasoning Complexity`: `12.27`, df `2`, `p=0.002`
- `Cognitive Process`: Wald chi-square `5.79`, df `4`, `p=0.215`
- `Universal Task Category`: Wald chi-square `0.58`, df `3`, `p=0.902`
- `QIC 1797.90`, `QICu 1798.01`

Supportive simplified model:

`Failure ~ Cognitive Process + Reasoning Complexity`

with:

- `Reasoning Complexity` still robust
- `Moderate vs Low`: aOR `5.44`, 95% CI `2.15-13.77`, `p<0.001`
- `High vs Low`: aOR `7.07`, 95% CI `1.67-29.96`, `p=0.008`
- `Apply vs Remember`: aOR `0.20`, 95% CI `0.06-0.74`, `p=0.015`
- joint Wald for `Cognitive Process`: `8.12`, df `4`, `p=0.087`
- `QIC 1797.21`, `QICu 1798.34`

Expanded exploratory model:

- should remain supplementary only
- not appropriate for the abstract or headline conclusion
- `QIC 1799.50`, `QICu 1807.02`
- poorer fit and unstable coefficients

**Recommended Abstract Rewrite**

Background: Large language model (LLM) accuracy on medical examinations may obscure clinically important reasoning failures. In neonatology, where diagnosis and management often depend on dynamic physiology and multi-step decision-making, evaluation beyond simple accuracy is essential. We aimed to identify item-level drivers of LLM failure using a non-English neonatal question set.

Methods: Eighteen contemporary LLMs were evaluated on 127 neonatal questions. Items were annotated using a neonatal taxonomy including cognitive process, reasoning complexity, and task category. Because multiple models answered the same question, clustered observations were analyzed using generalized estimating equations with question as the clustering unit. Model specification was assessed using collinearity diagnostics and QIC/QICu.

Results: Overall accuracy ranged from 68.5% to 96.85%. In the primary clustered GEE model, reasoning complexity was the only taxonomy domain independently associated with failure (Wald chi-square=12.27, df=2, p=0.002). Compared with low-complexity items, moderate-complexity items had 5.76-fold higher odds of failure (95% CI 2.14-15.48; p<0.001), and high-complexity items had 8.10-fold higher odds of failure (95% CI 1.82-36.11; p=0.006). Cognitive process and universal task category were not independently associated with failure.

Conclusions: LLM errors in neonatal question answering were driven predominantly by reasoning burden rather than by topic label alone. Aggregate accuracy may therefore overestimate safety in clinically demanding neonatal scenarios.

**Recommended Main Results Paragraph**

Across clustered analyses, reasoning complexity was the most consistent predictor of LLM failure. In the primary question-clustered GEE model including cognitive process, reasoning complexity, and universal task category, reasoning complexity was independently associated with failure (Wald chi-square=12.27, df=2, p=0.002), whereas cognitive process (Wald chi-square=5.79, df=4, p=0.215) and universal task category (Wald chi-square=0.58, df=3, p=0.902) were not. Relative to low-complexity items, moderate-complexity items had 5.76-fold higher odds of failure (95% CI 2.14-15.48; p<0.001), and high-complexity items had 8.10-fold higher odds of failure (95% CI 1.82-36.11; p=0.006). The primary model showed acceptable fit (QIC 1797.90; QICu 1798.01). In a supportive simplified clustered model including only cognitive process and reasoning complexity, the association with reasoning complexity remained robust, whereas the overall cognitive process effect remained non-significant at the joint-test level despite a lower odds of failure for `Apply` relative to `Remember`.

**Recommended Main Discussion Paragraph**

The central finding of this study is that reasoning complexity, rather than broad topic labeling, was the most reproducible determinant of LLM failure on neonatal questions. Questions requiring moderate or high reasoning complexity were consistently associated with markedly higher failure odds across clustered models. This is clinically relevant because neonatal decision-making rarely depends on factual recall alone; instead, it requires layered synthesis of physiology, diagnosis, risk assessment, and management. Our findings therefore suggest that high apparent exam-level accuracy may overstate the reliability of LLMs in the very neonatal scenarios where safe clinical reasoning matters most.

**Figure Plan**

Main manuscript:

- Figure 1: `forest_plot_primary_gee_journal.png`
- Figure 2: `graph_marginal_failure_by_complexity.png`
- Table 1: `Table1_Model_Accuracy.csv`
- Table 2: `Table2_Primary_GEE_Reduced_Model.csv`
- Table 3: `Table3_Primary_Wald_and_Fit.csv`

Supplement:

- Simplified model forest plot
- Expanded model forest plot
- QIC/QICu comparison
- Joint Wald comparison
- LPM sensitivity figure
- Verified collinearity figures
- Full model comparison tables

**Specific Supplement Corrections**

The current supplementary document should be revised as follows:

- Replace the statement `N=2,286 independent observations` with wording acknowledging repeated responses clustered within questions.
- Remove or rewrite the old `EPP` section unless you want to keep it purely as a descriptive adequacy check; if retained, make sure the event count is correct and clarify that clustered modeling was still necessary despite adequate event counts.
- Replace the old `QIC = 1926.61` and `1947.11` values with the validated QIC/QICu comparison tables already generated in the workspace.
- Remove the old Wald table reporting `Reasoning Complexity chi-square = 48.26` and `Cognitive Process p = 0.018`; those values do not match the final reproducible clustered models.
- Replace the old logistic-regression-oriented summary with the validated primary clustered GEE outputs.

**References To Use For Methods**

1. Liang KY, Zeger SL. Longitudinal data analysis using generalized linear models. *Biometrika*. 1986;73(1):13-22.
   Use for the GEE framework.

2. Pan W. Akaike's information criterion in generalized estimating equations. *Biometrics*. 2001;57(1):120-125. doi:10.1111/j.0006-341X.2001.00120.x
   Use for QIC.

3. Pan W. Model selection in estimating equations. *Biometrics*. 2001;57(2):529-534. doi:10.1111/j.0006-341X.2001.00529.x
   Use if you want to justify model comparison in GEE more broadly.

4. Peduzzi P, Concato J, Kemper E, Holford TR, Feinstein AR. A simulation study of the number of events per variable in logistic regression analysis. *J Clin Epidemiol*. 1996;49(12):1373-1379. doi:10.1016/S0895-4356(96)00236-3
   Use only if you retain an EPV/EPP statement.

5. Keles E, Bagci U. The past, current, and future of neonatal intensive care units with artificial intelligence: a systematic review. *npj Digit Med*. 2023;6:220. doi:10.1038/s41746-023-00941-5
   Use for neonatal AI context.

6. Yamada NK, Catchpole K, Salas E. The role of human factors in neonatal patient safety. *Semin Perinatol*. 2019;43(8):151174. doi:10.1053/j.semperi.2019.08.003
   Use for high-stakes reasoning and patient-safety context in neonatology.

**References To Use In Discussion**

- For AI in NICU / neonatal context: Keles and Bagci 2023.
- For neonatal patient safety / cognitive burden context: Yamada et al. 2019.
- For why overall performance can mask clinically meaningful errors, you can also cite your own framing paper if available or position this statement as an inference from the present data.

**Practical Recommendation**

For Neonatology, the cleanest structure is:

1. Accuracy as context only.
2. Clustered GEE as the main inferential method.
3. Reasoning complexity as the headline finding.
4. Cognitive process as a secondary, model-dependent finding.
5. Expanded full taxonomy model only in supplement.
