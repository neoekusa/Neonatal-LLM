"""Run figure and submission-package scripts after the core analysis."""

from analysis_data import validate_raw_data

import annotate_qic_models_and_family_plot
import make_clinical_domain_guideline_figures
import make_llm_family_clustering_plot
import make_spearman_error_heatmap
import make_verified_collinearity_figures
import prepare_neonatology_submission_package
import update_family_accuracy_dotplot_with_legend


STEPS = [
    ("family clustering source data", make_llm_family_clustering_plot.main),
    ("family accuracy dot plot", update_family_accuracy_dotplot_with_legend.main),
    ("Spearman error heatmap", make_spearman_error_heatmap.main),
    ("collinearity figures", make_verified_collinearity_figures.main),
    ("clinical domain and question-level figures", make_clinical_domain_guideline_figures.main),
    ("annotated QIC table and legacy family plot", annotate_qic_models_and_family_plot.main),
    ("submission package inventory", prepare_neonatology_submission_package.main),
]


def main():
    audit = validate_raw_data()
    print(f"Using scores: {audit.scores_path}")
    print(f"Using taxonomy: {audit.taxonomy_path}")
    for label, step in STEPS:
        print(f"\n=== {label} ===")
        step()


if __name__ == "__main__":
    main()
