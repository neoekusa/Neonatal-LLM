import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np
from _paths import OUTPUTS_DIR
from _model_labels import standardize_model_label

BASE = str(OUTPUTS_DIR)


def main():
    fam = pd.read_csv(f"{BASE}/llm_family_clustering_coordinates.csv")
    fam["Model"] = fam["Model"].map(standardize_model_label)
    colors = {
        "OpenAI": "#1f77b4",
        "Google": "#2ca02c",
        "Anthropic": "#ff7f0e",
        "xAI": "#d62728",
        "DeepSeek": "#9467bd",
        "Meta": "#8c564b",
    }
    order = (
        fam.groupby("Family")["Accuracy"]
        .mean()
        .sort_values(ascending=False)
        .index.tolist()
    )
    ypos = {fam_name: i for i, fam_name in enumerate(order)}

    fig, ax = plt.subplots(figsize=(10.8, 6.6))
    fam = fam.sort_values(["Family", "Accuracy"], ascending=[True, False]).reset_index(drop=True)
    offsets = {}
    for family_name, group in fam.groupby("Family", sort=False):
        n = len(group)
        if n == 1:
            offsets[family_name] = [0.0]
        else:
            offsets[family_name] = np.linspace(-0.24, 0.24, n).tolist()
    offsets["OpenAI"] = [-0.30, -0.18, -0.06, 0.06, 0.18, 0.30]

    family_seen = {family_name: 0 for family_name in order}
    default_label_y_offsets = [-0.055, -0.095, -0.040, -0.080, -0.120, -0.060]
    default_label_x_offsets = [-0.32, -0.46, -0.28, -0.42, -0.34, -0.50]
    family_label_offsets = {
        "OpenAI": {
            "x": [-0.36, -0.62, -0.30, -0.54, -0.24, -0.48],
            "y": [-0.020, -0.110, -0.045, -0.135, -0.080, -0.165],
        },
        "DeepSeek": {
            "x": [0.26, -0.30, -0.36],
            "y": [-0.020, -0.070, -0.020],
        },
    }
    model_label_overrides = {
        "DeepSeek-V3.2": {"dx": 0.40, "dy": -0.03, "ha": "left", "va": "top"},
        "DeepSeek-V4": {"dx": -0.34, "dy": -0.03, "ha": "right", "va": "top"},
    }
    openai_layout = {
        "ChatGPT-5": {"dx": -0.42, "dy": 0.10, "ha": "right", "va": "bottom"},
        "ChatGPT-5.4 Thinking": {"dx": 0.40, "dy": 0.12, "ha": "left", "va": "bottom"},
        "ChatGPT-4": {"dx": 0.40, "dy": 0.05, "ha": "left", "va": "bottom"},
        "ChatGPT-5.2": {"dx": 0.40, "dy": -0.02, "ha": "left", "va": "center"},
        "ChatGPT-5.4": {"dx": 0.40, "dy": -0.10, "ha": "left", "va": "top"},
        "ChatGPT-5.5 Thinking": {"dx": 0.40, "dy": -0.16, "ha": "left", "va": "top"},
    }

    for _, row in fam.iterrows():
        idx = family_seen[row["Family"]]
        y = ypos[row["Family"]] + offsets[row["Family"]][idx]
        offset_cfg = family_label_offsets.get(row["Family"], {})
        label_x_offsets = offset_cfg.get("x", default_label_x_offsets)
        label_y_offsets = offset_cfg.get("y", default_label_y_offsets)
        label_y = y + label_y_offsets[idx % len(label_y_offsets)]
        label_x = row["Accuracy"] + label_x_offsets[idx % len(label_x_offsets)]
        ha = "right"
        va = "top"
        if row["Model"] in openai_layout:
            override = openai_layout[row["Model"]]
            label_x = row["Accuracy"] + override["dx"]
            label_y = y + override["dy"]
            ha = override["ha"]
            va = override["va"]
        if row["Model"] in model_label_overrides:
            override = model_label_overrides[row["Model"]]
            label_x = row["Accuracy"] + override["dx"]
            label_y = y + override["dy"]
            ha = override["ha"]
            va = override["va"]
        family_seen[row["Family"]] += 1
        ax.scatter(
            row["Accuracy"],
            y,
            s=72,
            color=colors[row["Family"]],
            edgecolor="white",
            linewidth=0.8,
            alpha=0.95,
        )
        ax.text(
            label_x,
            label_y,
            row["Model"],
            ha=ha,
            va=va,
            fontsize=8,
        )

    handles = [
        Line2D(
            [0], [0],
            marker="o",
            color="none",
            markerfacecolor=colors[f],
            markeredgecolor="white",
            markeredgewidth=0.8,
            markersize=8,
            label=f,
        )
        for f in order
    ]
    ax.legend(
        handles=handles,
        title="Family",
        frameon=False,
        loc="upper left",
        bbox_to_anchor=(1.01, 1.0),
        ncol=1,
        fontsize=8,
        title_fontsize=9,
    )

    ax.set_yticks(list(ypos.values()))
    ax.set_yticklabels(order)
    ax.set_xlabel("Accuracy Rate (%)")
    ax.set_ylabel("Language Model Family")
    ax.grid(axis="x", linestyle=":", alpha=0.35)
    ax.set_xlim(fam["Accuracy"].min() - 3.5, fam["Accuracy"].max() + 8.5)
    plt.tight_layout(rect=[0, 0, 0.84, 1])
    plt.savefig(f"{BASE}/graph_accuracy_rate_by_language_family_dotplot_legend.png", dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved {BASE}/graph_accuracy_rate_by_language_family_dotplot_legend.png")


if __name__ == "__main__":
    main()
