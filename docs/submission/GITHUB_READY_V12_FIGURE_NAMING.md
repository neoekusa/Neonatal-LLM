# GitHub-Ready Figure Naming Status (`v12`)

This note documents the figure-label naming convention currently used in the repository for the `v12` score file:

- Local source file used for the latest figure refresh:
  - `/Users/bagcilab/Downloads/YDUS_LLM_KEYS_all_LLMS _EK_v12_may_son.csv`
- Repository score link currently points to:
  - `data/raw/ydus_llm_scores.csv`

## Current Visible Model Names on Figures

The following model names are the current display labels used across the updated figures:

- `ChatGPT-5`
- `Gemini 3 Pro`
- `Claude Sonnet 4.5`
- `ChatGPT-5.2`
- `Claude Sonnet 3.5`
- `Gemini 2.5 Pro`
- `DeepSeek-V3`
- `ChatGPT-4`
- `Claude Sonnet 4.6`
- `DeepSeek-V3.2`
- `Gemini 3.1 Pro`
- `ChatGPT-5.4 Thinking`
- `Grok 4.2`
- `Llama 4`
- `ChatGPT-5.4`
- `Llama 3.3`
- `Grok 4`
- `Gemma 4`
- `ChatGPT-5.5 Thinking`
- `DeepSeek-V4`

## Figures Refreshed with This Naming

- `outputs/graph_accuracy_rate_by_language_family_dotplot_legend.png`
- `outputs/figure_inter_model_error_correlation_heatmap.png`
- `outputs/figure_cross_model_error_patterns_main_domains.png`
- `outputs/figure_question_level_correctness_matrix.png`
- `outputs/figure_question_level_incorrect_at_least_1.png`
- `outputs/figure_question_level_incorrect_at_least_10.png`

## Implementation Notes

- Display-name harmonization is controlled by:
  - `scripts/_model_labels.py`
- The language-family accuracy dot plot layout is controlled by:
  - `scripts/update_family_accuracy_dotplot_with_legend.py`
- Question-level and domain-level figures are generated from:
  - `scripts/make_clinical_domain_guideline_figures.py`
- The inter-model correlation heatmap is generated from:
  - `scripts/make_spearman_error_heatmap.py`

## GitHub Sharing Note

If the repository is pushed publicly, the local absolute source path above should be treated as provenance only. Reproduction on another machine should use:

- `data/raw/ydus_llm_scores.csv`

with a compatible CSV placed there by the user.
