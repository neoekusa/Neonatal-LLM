# Neonatal LLM benchmark v4

This release analyzes 127 neonatal examination questions answered by 20 labeled web-model series. There are 2,540 recorded responses and 351 disagreements with the supplied keys. In the primary question-clustered analysis, the adjusted odds ratio for failure on high- versus low-complexity items is **7.59** (95% CI 1.77–32.55, p = 0.0064). The unit of taxonomy replication is the question. The comparison applies to this recorded panel and set of examination items.


## Reproduce the results

The authors confirmed that `RealAnswer` in the supplied score sheet contains the original answer key for all 127 questions. The loader reads the 20 response columns from that same file and applies the authors’ ChatGPT-4o correction on import. Item classifications come from the supplied taxonomy. The primary run counts two `NR` records and one `Selected all` record as incorrect. The loader rejects unrecognized responses, repeated question numbers, duplicate model labels and mismatched question sets. [Score sheet](data/raw/ydus_llm_scores.csv) · [Taxonomy](data/raw/taxonomy_annotations.csv)

Python 3.12.13, R 4.2.2 and lme4 1.1-31 were used for verification. Python dependencies are pinned in [requirements.txt](requirements.txt). The full workflow needs `Rscript` and the R package `lme4`. The launchers support Linux and macOS.

```sh
./setup_linux.sh                 # or ./setup_macos.sh
Rscript -e 'install.packages("lme4", repos="https://cloud.r-project.org")'  # if needed
.venv/bin/python scripts/run_core_pipeline.py --with-figures
```

The full command writes the tables, four figure PNGs and the [run manifest](outputs/v4/run_manifest.json) into `outputs/v4/`. Running the core script without `--with-figures` produces a fresh tables-only directory. Use `scripts/run_figure_pipeline.py` to add the figures from those tables. `--python-only` explicitly omits the R fit and records that omission in the manifest. A failed fit or missing required R dependency leaves the previously published results in place. Native R/lme4 builds can differ slightly in the last digits of Hessian-based confidence limits.

With Tk installed, `.venv/bin/python main.py` opens the existing graphical runner. For custom installations set `NEO_RSCRIPT` to the Rscript executable. The input options `NEO_SCORES_CSV` and `NEO_TAXONOMY_CSV` select alternate input CSVs within the repository.

## Interpret the tables

| Question | Result files and interpretation |
|---|---|
| How accurate was each recorded series? | [Accuracy with Wilson intervals](outputs/v4/accuracy.csv), [paired Cochran Q](outputs/v4/cochran_q.csv), [non-single answers](outputs/v4/non_single_responses.csv), [question correctness](outputs/v4/question_correctness.csv). Error correlations describe shared response patterns. |
| Where do the data support comparisons? | [Observed categories](outputs/v4/observed_by_category.csv), [complexity by cognitive process](outputs/v4/complexity_by_cognitive.csv), [primary three-way table](outputs/v4/primary_strata.csv), [full six-way table](outputs/v4/full_strata.csv), [support summary](outputs/v4/strata_summary.csv). Counts include empty cells. Their failure rates are undefined. |
| Which predictors are associated with failure? | [Primary coefficients](outputs/v4/primary_coefficients.csv) and [joint Wald tests](outputs/v4/primary_wald.csv). Binomial logit GEE, clustered by question, exchangeable working correlation, robust covariance. Predictors are cognitive process, complexity and task. Raw contrast p-values are labeled separately from the Holm adjustment for cognitive contrasts. |
| What are the absolute risks? | [Marginal risks](outputs/v4/marginals.csv) and [risk differences](outputs/v4/marginal_differences.csv). For each level of complexity, average predicted risks over the 127 observed cognitive-process and task profiles. The intervals use the robust delta method with that case mix held fixed. Predictions outside observed combinations rely on the additive specification. |
| How sensitive is the result? | [Sensitivity coefficients](outputs/v4/sensitivity_coefficients.csv), [joint tests](outputs/v4/sensitivity_wald.csv), [leave-one-series-out estimates](outputs/v4/leave_one_model_out.csv), [clustered linear probability model](outputs/v4/linear_probability.csv) and [crossed random intercepts for question and series](outputs/v4/crossed_random_effects.csv). The crossed odds ratios are conditional on question and series random effects. |
| Which full-model results are estimable? | [Design ranks and fit](outputs/v4/gee_model_fit.csv), [categorical overlap](outputs/v4/cramers_v.csv) and [reference-coded VIFs](outputs/v4/primary_dummy_vif.csv). Evaluate and Metacognitive coincide on five items. The six-factor design has rank 17/18. Its coefficient, Wald and QIC cells are omitted. Compare QIC or QICu only for models fitted to the same responses and outcome definition. |
| Which distractors did the series select on difficult items? | [Consensus counts, all wrong options and ties](outputs/v4/consensus_items.csv), [pairwise error correlations](outputs/v4/error_pairs.csv), and the [item review](docs/consensus_item_review_v4.md). The item review gives the recorded key, taxonomy and counts for each incorrect response across the 20 series. |

The [pilot item list](pilot/pilot_item_list.csv) contains 28 candidate questions. The file contains item selections and descriptive annotations. It contains no human, translation, repeated-trial, alternate-prompt or open-ended outcomes. These questions enter the main analysis on the same terms as the other 99.

After a full run, execute `.venv/bin/python -m unittest discover -s tests -v` for the v4 regression checks covering label normalization, paired scoring, the robust primary interval and zero-inclusive strata.
