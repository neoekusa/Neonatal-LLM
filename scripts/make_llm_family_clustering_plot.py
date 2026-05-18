import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from _paths import OUTPUTS_DIR, RAW_SCORES
from _model_labels import standardize_model_label

BASE = str(OUTPUTS_DIR)
SCORES = str(RAW_SCORES)


FAMILY_MAP = {
    "Gemini3.1Pro": "Google",
    "Gemini2.5Pro": "Google",
    "Gemini3Pro": "Google",
    "Gemma4": "Google",
    "Chat5.4": "OpenAI",
    "Chat5.4Thinking": "OpenAI",
    "GPT 5.5 Thinking": "OpenAI",
    "ChatGPT5.2": "OpenAI",
    "ChatGPT4": "OpenAI",
    "ChatGPT5": "OpenAI",
    "ClaudeSonnet4.5": "Anthropic",
    "ClaudeSonnet4.6": "Anthropic",
    "Claude Sonnet 3.5": "Anthropic",
    "Grok4": "xAI",
    "Grok4.2": "xAI",
    "DeepSeekv3": "DeepSeek",
    "DeepSeek3.2": "DeepSeek",
    "DeepseekV4": "DeepSeek",
    "Llama4": "Meta",
    "Llama3.3": "Meta",
}

FAMILY_MAP.update(
    {standardize_model_label(key): value for key, value in list(FAMILY_MAP.items())}
)


COLORS = {
    "OpenAI": "#1f77b4",
    "Google": "#2ca02c",
    "Anthropic": "#ff7f0e",
    "xAI": "#d62728",
    "DeepSeek": "#9467bd",
    "Meta": "#8c564b",
}


def classical_mds(distance_matrix, n_components=2):
    n = distance_matrix.shape[0]
    h = np.eye(n) - np.ones((n, n)) / n
    b = -0.5 * h @ (distance_matrix ** 2) @ h
    eigvals, eigvecs = np.linalg.eigh(b)
    idx = np.argsort(eigvals)[::-1]
    eigvals = eigvals[idx]
    eigvecs = eigvecs[:, idx]
    pos = np.maximum(eigvals[:n_components], 0)
    coords = eigvecs[:, :n_components] * np.sqrt(pos)
    return coords


def main():
    scores_df = pd.read_csv(SCORES)
    scores_df.columns = [c.strip() for c in scores_df.columns]
    model_cols = [c for c in scores_df.columns if c not in ["Number", "RealAnswer"]]

    error_matrix = pd.DataFrame(index=scores_df["Number"])
    for model in model_cols:
        error_matrix[model] = (
            scores_df[model].astype(str).str.strip() != scores_df["RealAnswer"].astype(str).str.strip()
        ).astype(int)

    corr = error_matrix.corr(method="spearman")
    dist = 1 - corr
    coords = classical_mds(dist.values, n_components=2)

    accuracy = []
    for model in model_cols:
        acc = (1 - error_matrix[model].mean()) * 100
        accuracy.append(acc)

    standardized_models = [standardize_model_label(model) for model in model_cols]
    plot_df = pd.DataFrame(
        {
            "Model": standardized_models,
            "Dim1": coords[:, 0],
            "Dim2": coords[:, 1],
            "Family": [FAMILY_MAP.get(m, "Other") for m in standardized_models],
            "Accuracy": accuracy,
        }
    )
    plot_df.to_csv(f"{BASE}/llm_family_clustering_coordinates.csv", index=False)

    fig, ax = plt.subplots(figsize=(9, 7))
    for family, grp in plot_df.groupby("Family"):
        ax.scatter(
            grp["Dim1"],
            grp["Dim2"],
            s=65,
            color=COLORS.get(family, "#333333"),
            label=family,
            alpha=0.9,
            edgecolor="white",
            linewidth=0.7,
        )
        for _, row in grp.iterrows():
            ax.text(row["Dim1"] + 0.01, row["Dim2"] + 0.01, row["Model"], fontsize=8)

    ax.set_xlabel("MDS Dimension 1")
    ax.set_ylabel("MDS Dimension 2")
    ax.grid(linestyle=":", alpha=0.35)
    ax.legend(title="LLM Family", frameon=False, loc="best")
    plt.tight_layout()
    plt.savefig(f"{BASE}/graph_llm_family_clustering.png", dpi=300, bbox_inches="tight")
    plt.close(fig)

    # Also a cleaner family-level dot plot for accuracy
    order = (
        plot_df.groupby("Family")["Accuracy"]
        .mean()
        .sort_values(ascending=False)
        .index.tolist()
    )
    fig, ax = plt.subplots(figsize=(8.5, 5.8))
    y_pos = {fam: i for i, fam in enumerate(order)}
    rng = np.random.default_rng(42)
    jitter = rng.uniform(-0.12, 0.12, size=len(plot_df))
    for i, (_, row) in enumerate(plot_df.iterrows()):
        ax.scatter(
            row["Accuracy"],
            y_pos[row["Family"]] + jitter[i],
            s=65,
            color=COLORS.get(row["Family"], "#333333"),
            edgecolor="white",
            linewidth=0.7,
        )
        ax.text(row["Accuracy"] + 0.3, y_pos[row["Family"]] + jitter[i], row["Model"], va="center", fontsize=8)

    ax.set_yticks(list(y_pos.values()))
    ax.set_yticklabels(order)
    ax.set_xlabel("Accuracy (%)")
    ax.set_ylabel("LLM Family")
    ax.grid(axis="x", linestyle=":", alpha=0.35)
    plt.tight_layout()
    plt.savefig(f"{BASE}/graph_llm_family_accuracy_dotplot.png", dpi=300, bbox_inches="tight")
    plt.close(fig)

    print(f"Saved {BASE}/llm_family_clustering_coordinates.csv")
    print(f"Saved {BASE}/graph_llm_family_clustering.png")
    print(f"Saved {BASE}/graph_llm_family_accuracy_dotplot.png")


if __name__ == "__main__":
    main()
