import shutil

import pandas as pd
from _paths import DOCS_DIR, OUTPUTS_DIR

BASE = str(OUTPUTS_DIR)
SUBMISSION_DIR = DOCS_DIR / "submission"


def main():
    main_figures = [
        {
            "slot": "Figure 1",
            "file": "forest_plot_primary_gee_journal.png",
            "purpose": "Primary clustered GEE forest plot",
            "manuscript_section": "Main manuscript",
            "legend": (
                "Forest plot of adjusted odds ratios for failure from the primary question-clustered "
                "GEE model. Reference categories were Remember for cognitive process, Low for "
                "reasoning complexity, and Physiology and Pathophysiology for universal task "
                "category. Error bars indicate 95% confidence intervals."
            ),
        },
        {
            "slot": "Figure 2",
            "file": "graph_marginal_failure_by_complexity.png",
            "purpose": "Marginal predicted failure risk by reasoning complexity",
            "manuscript_section": "Main manuscript",
            "legend": (
                "Model-based marginal predicted probability of failure from the primary "
                "question-clustered GEE model across reasoning-complexity strata."
            ),
        },
    ]

    supplement_figures = [
        {
            "slot": "Supplementary Figure 1",
            "file": "forest_plot_cognitive_complexity_journal.png",
            "purpose": "Supportive clustered GEE with cognitive process and complexity only",
            "manuscript_section": "Supplement",
            "legend": (
                "Forest plot of the supportive simplified clustered GEE model including only "
                "cognitive process and reasoning complexity."
            ),
        },
        {
            "slot": "Supplementary Figure 2",
            "file": "full_exploratory_remember_forest.png",
            "purpose": "Expanded exploratory full-taxonomy GEE forest plot",
            "manuscript_section": "Supplement",
            "legend": (
                "Forest plot from the expanded exploratory clustered GEE model including "
                "knowledge dimension, cognitive process, reasoning complexity, clinical risk, "
                "difficulty, and universal task category."
            ),
        },
        {
            "slot": "Supplementary Figure 3",
            "file": "full_exploratory_collapsed_forest_publication.png",
            "purpose": "Collapsed sparse-category exploratory sensitivity forest plot",
            "manuscript_section": "Supplement",
            "legend": (
                "Sensitivity forest plot after collapsing sparse metacognitive and evaluate "
                "categories into adjacent taxonomy groups."
            ),
        },
        {
            "slot": "Supplementary Figure 4",
            "file": "verified_cramers_v_matrix.png",
            "purpose": "Verified categorical collinearity matrix",
            "manuscript_section": "Supplement",
            "legend": (
                "Verified Cramer's V matrix showing the degree of association among taxonomy "
                "predictors."
            ),
        },
        {
            "slot": "Supplementary Figure 5",
            "file": "verified_vif_values.png",
            "purpose": "Verified VIF plot",
            "manuscript_section": "Supplement",
            "legend": (
                "Verified variance inflation factor values for taxonomy predictors used to assess "
                "multicollinearity."
            ),
        },
        {
            "slot": "Supplementary Figure 6",
            "file": "figure_inter_model_error_correlation_heatmap.png",
            "purpose": "Inter-model error correlation heatmap",
            "manuscript_section": "Supplement",
            "legend": (
                "Spearman correlation heatmap comparing model-level error patterns across "
                "questions."
            ),
        },
        {
            "slot": "Supplementary Figure 7",
            "file": "figure_cross_model_error_patterns_main_domains.png",
            "purpose": "Cross-model error patterns across main clinical domains",
            "manuscript_section": "Supplement",
            "legend": (
                "Heatmap of model-specific error rates across main clinical domains, with models "
                "grouped by family."
            ),
        },
    ]

    main_tables = [
        {
            "slot": "Table 1",
            "file": "Table1_Model_Accuracy.csv",
            "purpose": "Model accuracy summary",
            "manuscript_section": "Main manuscript",
            "legend": "Overall accuracy of each language model across the full neonatal question set.",
        },
        {
            "slot": "Table 2",
            "file": "Table2_Primary_GEE_Reduced_Model.csv",
            "purpose": "Primary clustered GEE coefficient table",
            "manuscript_section": "Main manuscript",
            "legend": (
                "Primary question-clustered GEE model examining associations between taxonomy "
                "features and model failure."
            ),
        },
        {
            "slot": "Table 3",
            "file": "Table3_Primary_Wald_and_Fit.csv",
            "purpose": "Joint Wald tests and fit statistics for primary model",
            "manuscript_section": "Main manuscript",
            "legend": (
                "Joint Wald chi-square tests and model-fit statistics for the primary reduced "
                "clustered GEE model."
            ),
        },
    ]

    supplement_tables = [
        {
            "slot": "Supplementary Table 1",
            "file": "TableS1_Expanded_Exploratory_GEE.csv",
            "purpose": "Expanded exploratory GEE results",
            "manuscript_section": "Supplement",
            "legend": (
                "Expanded exploratory clustered GEE model including knowledge dimension, cognitive "
                "process, reasoning complexity, clinical risk, difficulty, and universal task "
                "category."
            ),
        },
        {
            "slot": "Supplementary Table 2",
            "file": "TableS2_Consensus_Hard_Questions.csv",
            "purpose": "Consensus hard questions",
            "manuscript_section": "Supplement",
            "legend": "Questions missed by at least five models, with taxonomy annotations.",
        },
        {
            "slot": "Supplementary Table 3",
            "file": "comparison_previous_vs_cognitive_complexity_model.csv",
            "purpose": "Primary versus simplified model comparison",
            "manuscript_section": "Supplement",
            "legend": (
                "Comparison of the primary clustered GEE model and the simplified cognitive "
                "process plus reasoning complexity model."
            ),
        },
        {
            "slot": "Supplementary Table 4",
            "file": "all_model_qic_qicu_comparison.csv",
            "purpose": "QIC/QICu comparison across all candidate models",
            "manuscript_section": "Supplement",
            "legend": (
                "QIC and QICu comparison across all candidate clustered GEE model specifications."
            ),
        },
        {
            "slot": "Supplementary Table 5",
            "file": "full_model_reference_qic_check.csv",
            "purpose": "Reference-category QIC diagnostic",
            "manuscript_section": "Supplement",
            "legend": (
                "Reference-coding diagnostic for the expanded full-taxonomy model. "
                "QIC and QICu are reported as positive model-fit criteria. The diagnostic "
                "also includes quasi-likelihood, explicitly labeled as not QIC, because it "
                "can be negative. Recoded fits are not treated as separate model-ranking entries."
            ),
        },
        {
            "slot": "Supplementary Table 6",
            "file": "clean_gee_lpm_vif.csv",
            "purpose": "VIF for simplified cognitive-complexity model",
            "manuscript_section": "Supplement",
            "legend": (
                "Variance inflation factor values for dummy-coded terms in the simplified cognitive "
                "process plus reasoning complexity model."
            ),
        },
        {
            "slot": "Supplementary Table 7",
            "file": "verified_cramers_v_matrix.csv",
            "purpose": "Verified Cramer's V source matrix",
            "manuscript_section": "Supplement",
            "legend": "Source Cramer's V matrix underlying the categorical collinearity heatmap.",
        },
        {
            "slot": "Supplementary Table 8",
            "file": "verified_vif_values.csv",
            "purpose": "Verified VIF source table",
            "manuscript_section": "Supplement",
            "legend": "Source variance inflation factor values underlying the verified VIF plot.",
        },
    ]

    inventory = pd.DataFrame(main_figures + supplement_figures + main_tables + supplement_tables)
    inventory.to_csv(f"{BASE}/Neonatology_Submission_Inventory.csv", index=False)

    with open(f"{BASE}/Neonatology_Submission_Package.md", "w", encoding="utf-8") as fh:
        fh.write("# Neonatology Submission Package\n\n")
        fh.write("## Main Manuscript Figures\n\n")
        for item in main_figures:
            fh.write(f"- {item['slot']}: `{item['file']}`\n")
            fh.write(f"  Purpose: {item['purpose']}\n")
            fh.write(f"  Legend: {item['legend']}\n\n")

        fh.write("## Supplementary Figures\n\n")
        for item in supplement_figures:
            fh.write(f"- {item['slot']}: `{item['file']}`\n")
            fh.write(f"  Purpose: {item['purpose']}\n")
            fh.write(f"  Legend: {item['legend']}\n\n")

        fh.write("## Main Manuscript Tables\n\n")
        for item in main_tables:
            fh.write(f"- {item['slot']}: `{item['file']}`\n")
            fh.write(f"  Purpose: {item['purpose']}\n")
            fh.write(f"  Legend: {item['legend']}\n\n")

        fh.write("## Supplementary Tables\n\n")
        for item in supplement_tables:
            fh.write(f"- {item['slot']}: `{item['file']}`\n")
            fh.write(f"  Purpose: {item['purpose']}\n")
            fh.write(f"  Legend: {item['legend']}\n\n")

        fh.write("## Statistical Narrative\n\n")
        fh.write(
            "Primary inference is based on the reduced question-clustered GEE model including "
            "cognitive process, reasoning complexity, and universal task category. The main "
            "finding is that reasoning complexity is the most robust predictor of failure. "
            "Expanded taxonomy models are retained as supplementary exploratory analyses because "
            "they show poorer fit and unstable coefficients.\n"
        )

    print(f"Saved {BASE}/Neonatology_Submission_Inventory.csv")
    print(f"Saved {BASE}/Neonatology_Submission_Package.md")

    SUBMISSION_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copy(
        f"{BASE}/Neonatology_Submission_Inventory.csv",
        SUBMISSION_DIR / "Neonatology_Submission_Inventory.csv",
    )
    shutil.copy(
        f"{BASE}/Neonatology_Submission_Package.md",
        SUBMISSION_DIR / "Neonatology_Submission_Package.md",
    )
    print(f"Updated {SUBMISSION_DIR}/Neonatology_Submission_Inventory.csv")
    print(f"Updated {SUBMISSION_DIR}/Neonatology_Submission_Package.md")


if __name__ == "__main__":
    main()
