import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from _paths import OUTPUTS_DIR
from _model_labels import standardize_model_label

BASE = str(OUTPUTS_DIR)
INPUT = f"{BASE}/TableS12_Spearman_Error_Correlation.csv"
OUTPUT = f"{BASE}/figure_inter_model_error_correlation_heatmap.png"
FAMILY_INPUT = f"{BASE}/llm_family_clustering_coordinates.csv"


def ordered_labels(corr: pd.DataFrame) -> list[str]:
    fam = pd.read_csv(FAMILY_INPUT)
    fam["Model"] = fam["Model"].map(standardize_model_label)
    family_order = ["OpenAI", "Google", "Anthropic", "xAI", "DeepSeek", "Meta"]
    fam["family_rank"] = fam["Family"].map({name: i for i, name in enumerate(family_order)})
    fam = fam.sort_values(["family_rank", "Accuracy"], ascending=[True, False])
    labels = [label for label in fam["Model"].tolist() if label in corr.index]
    remaining = [label for label in corr.index if label not in labels]
    return labels + remaining


def main():
    corr = pd.read_csv(INPUT, index_col=0)
    corr.index = [standardize_model_label(label) for label in corr.index]
    corr.columns = [standardize_model_label(label) for label in corr.columns]
    order = ordered_labels(corr)
    corr = corr.loc[order, order]

    fig, ax = plt.subplots(figsize=(13, 11))
    ax = sns.heatmap(
        corr,
        cmap="RdYlBu_r",
        vmin=0,
        vmax=1,
        square=True,
        linewidths=0.4,
        linecolor="white",
        cbar=True,
        annot=False,
        ax=ax,
    )

    for i in range(corr.shape[0]):
        for j in range(corr.shape[1]):
            val = corr.iloc[i, j]
            text_color = "black" if val < 0.65 else "white"
            ax.text(
                j + 0.5,
                i + 0.5,
                f"{val:.2f}",
                ha="center",
                va="center",
                fontsize=7,
                color=text_color,
            )

    ax.set_xlabel("")
    ax.set_ylabel("")
    ax.set_xticks([i + 0.5 for i in range(corr.shape[1])])
    ax.set_yticks([i + 0.5 for i in range(corr.shape[0])])
    ax.set_xticklabels(corr.columns, rotation=45, ha="right", rotation_mode="anchor", fontsize=8)
    ax.set_yticklabels(corr.index, rotation=0, fontsize=8)
    ax.tick_params(axis="x", pad=4)
    ax.tick_params(axis="y", pad=4)

    fig.subplots_adjust(left=0.16, bottom=0.18, right=0.98, top=0.98)
    fig.savefig(OUTPUT, dpi=300, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    main()
