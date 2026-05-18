import pandas as pd
import matplotlib.pyplot as plt
from _paths import OUTPUTS_DIR

BASE = str(OUTPUTS_DIR)


MODEL_FORMULAS = {
    "minus_knowledge_difficulty_clinicalrisk": "Failure ~ Cognitive Process + Reasoning Complexity + Universal Task Category (question-clustered GEE)",
    "minus_knowledge_difficulty": "Failure ~ Cognitive Process + Reasoning Complexity + Clinical Risk + Universal Task Category (question-clustered GEE)",
    "minus_knowledge": "Failure ~ Cognitive Process + Reasoning Complexity + Clinical Risk + Difficulty + Universal Task Category (question-clustered GEE)",
    "reduced_cognitive_complexity_only": "Failure ~ Cognitive Process + Reasoning Complexity (question-clustered GEE)",
    "primary_reduced_cognitive_complexity_task": "Failure ~ Cognitive Process + Reasoning Complexity + Universal Task Category (question-clustered GEE; primary model)",
    "full_taxonomy_remember_reference": "Failure ~ Knowledge Dimension + Cognitive Process + Reasoning Complexity + Clinical Risk + Difficulty + Universal Task Category (question-clustered GEE; Remember reference)",
}


def main():
    qic = pd.read_csv(f"{BASE}/TableS4_QIC_QICu_Model_Comparison.csv")
    qic["formula_description"] = qic["model_spec"].map(MODEL_FORMULAS).fillna(qic["model_spec"])
    qic["display_label"] = qic.apply(
        lambda r: f"{r['model_spec']} ({r['formula_description']})", axis=1
    )
    qic.to_csv(f"{BASE}/TableS4_QIC_QICu_Model_Comparison_Annotated.csv", index=False)

    fam = pd.read_csv(f"{BASE}/llm_family_clustering_coordinates.csv")
    fam["Family_Display"] = fam["Family"].replace(
        {
            "OpenAI": "OpenAI",
            "Google": "Google",
            "Anthropic": "Anthropic",
            "xAI": "xAI",
            "DeepSeek": "DeepSeek",
            "Meta": "Meta",
        }
    )
    colors = {
        "OpenAI": "#1f77b4",
        "Google": "#2ca02c",
        "Anthropic": "#ff7f0e",
        "xAI": "#d62728",
        "DeepSeek": "#9467bd",
        "Meta": "#8c564b",
    }
    order = (
        fam.groupby("Family_Display")["Accuracy"]
        .mean()
        .sort_values(ascending=False)
        .index.tolist()
    )
    ypos = {fam_name: i for i, fam_name in enumerate(order)}

    fig, ax = plt.subplots(figsize=(8.8, 5.8))
    fam = fam.sort_values(["Family_Display", "Accuracy"], ascending=[True, False]).reset_index(drop=True)
    jitter = [-0.16, -0.08, 0.0, 0.08, 0.16, -0.12, 0.12, -0.04, 0.04]
    for i, (_, row) in enumerate(fam.iterrows()):
        y = ypos[row["Family_Display"]] + jitter[i % len(jitter)]
        ax.scatter(
            row["Accuracy"],
            y,
            s=70,
            color=colors[row["Family_Display"]],
            edgecolor="white",
            linewidth=0.8,
        )
        ax.text(row["Accuracy"] + 0.25, y, row["Model"], va="center", fontsize=8)

    ax.set_yticks(list(ypos.values()))
    ax.set_yticklabels(order)
    ax.set_xlabel("Accuracy Rate (%)")
    ax.set_ylabel("Language Model Family")
    ax.grid(axis="x", linestyle=":", alpha=0.35)
    plt.tight_layout()
    plt.savefig(f"{BASE}/graph_accuracy_rate_by_language_family_dotplot.png", dpi=300, bbox_inches="tight")
    plt.close(fig)

    print(f"Saved {BASE}/TableS4_QIC_QICu_Model_Comparison_Annotated.csv")
    print(f"Saved {BASE}/graph_accuracy_rate_by_language_family_dotplot.png")


if __name__ == "__main__":
    main()
