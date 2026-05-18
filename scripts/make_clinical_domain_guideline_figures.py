import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Patch, Rectangle
from matplotlib.colors import LinearSegmentedColormap
from _paths import OUTPUTS_DIR, RAW_SCORES, RAW_TAXONOMY
from _model_labels import standardize_model_label, standardize_model_labels

BASE = str(OUTPUTS_DIR)
SCORES = str(RAW_SCORES)
TAXONOMY = str(RAW_TAXONOMY)


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

FAMILY_COLORS = {
    "OpenAI": "#1f77b4",
    "Google": "#2ca02c",
    "Anthropic": "#ff7f0e",
    "xAI": "#d62728",
    "DeepSeek": "#9467bd",
    "Meta": "#8c564b",
}

GUIDELINE_GROUP_COLORS = {
    "AAP/American Academy": "#1f77b4",
    "AHA/PALS/Cardiology": "#d62728",
    "CDC/Red Book/Infectious": "#2ca02c",
    "Genetics/Genomics": "#9467bd",
    "Endocrine/Metabolic": "#ff7f0e",
    "Perinatal/Obstetric": "#8c564b",
    "Renal/Heme/Specialty Society": "#e377c2",
    "Basic Science": "#7f7f7f",
    "Institutional/Local": "#bcbd22",
    "Other/Unspecified": "#17becf",
}


def guideline_group(text: str) -> str:
    t = str(text).strip().lower()
    if "aap" in t:
        return "AAP/American Academy"
    if "aha" in t or "pals" in t or "cardiology" in t:
        return "AHA/PALS/Cardiology"
    if "red book" in t or "cdc" in t:
        return "CDC/Red Book/Infectious"
    if "acmg" in t or "genetics" in t or "database" in t:
        return "Genetics/Genomics"
    if "espe" in t or "metabolism" in t or "manual" in t:
        return "Endocrine/Metabolic"
    if "smfm" in t or "perinatal" in t or "ballard" in t:
        return "Perinatal/Obstetric"
    if "ipna" in t or "isth" in t or "surgery" in t or "fda" in t:
        return "Renal/Heme/Specialty Society"
    if "basic science" in t:
        return "Basic Science"
    if "institution" in t or "local" in t or "hospital" in t or "unit" in t or "nicu" in t or "protocol" in t:
        return "Institutional/Local"
    return "Other/Unspecified"


def load_data():
    scores = pd.read_csv(SCORES)
    tax = pd.read_csv(TAXONOMY)
    scores.columns = [c.strip() for c in scores.columns]
    tax.columns = [c.strip() for c in tax.columns]
    return scores, tax


def make_content_distribution_figure(tax: pd.DataFrame):
    domain = tax["Main Domain"].astype(str).str.strip().value_counts().sort_values(ascending=False)
    raw_guidelines = tax["Main Guideline"].astype(str).str.strip()

    def harmonize_guideline_label(label: str) -> str:
        t = str(label).strip()
        tl = t.lower()
        if "aap" in tl:
            return "AAP Guidelines"
        if "aha" in tl or "pals" in tl or "cardiology" in tl:
            return "AHA/PALS/Cardiology"
        if "cdc" in tl or "red book" in tl:
            return "CDC/Red Book"
        if "acmg" in tl or "genetics database" in tl or "genetics" in tl:
            return "ACMG/Genetics"
        return t

    raw_guidelines = raw_guidelines.map(harmonize_guideline_label)
    guideline_counts = raw_guidelines.value_counts()
    guideline_df = guideline_counts.rename_axis("Main Guideline").reset_index(name="Count")
    guideline_df["Guideline Group"] = guideline_df["Main Guideline"].map(guideline_group)
    guideline_df["Percent"] = 100 * guideline_df["Count"] / guideline_df["Count"].sum()

    group_order = [
        "AAP/American Academy",
        "AHA/PALS/Cardiology",
        "CDC/Red Book/Infectious",
        "Genetics/Genomics",
        "Endocrine/Metabolic",
        "Perinatal/Obstetric",
        "Renal/Heme/Specialty Society",
        "Basic Science",
        "Institutional/Local",
        "Other/Unspecified",
    ]
    guideline_df["group_rank"] = guideline_df["Guideline Group"].map({g: i for i, g in enumerate(group_order)}).fillna(999)
    guideline_df = guideline_df.sort_values(["group_rank", "Count", "Main Guideline"], ascending=[True, False, True]).reset_index(drop=True)

    domain_df = domain.rename_axis("Main Domain").reset_index(name="Count")
    domain_df.to_csv(f"{BASE}/clinical_domain_distribution.csv", index=False)
    guideline_df.to_csv(f"{BASE}/guideline_source_family_distribution.csv", index=False)

    fig, axes = plt.subplots(1, 2, figsize=(14, 10), gridspec_kw={"width_ratios": [1.25, 1]})

    axes[0].barh(domain_df["Main Domain"], domain_df["Count"], color="#4C78A8")
    axes[0].invert_yaxis()
    axes[0].set_xlabel("Number of Questions")
    axes[0].grid(axis="x", linestyle=":", alpha=0.35)

    colors = [GUIDELINE_GROUP_COLORS[g] for g in guideline_df["Guideline Group"]]
    axes[1].barh(guideline_df["Main Guideline"], guideline_df["Count"], color=colors)
    axes[1].invert_yaxis()
    for i, row in guideline_df.iterrows():
        axes[1].text(row["Count"] + 0.2, i, f"{row['Count']} ({row['Percent']:.1f}%)", va="center", fontsize=9)
    axes[1].set_xlabel("Number of Questions")
    axes[1].grid(axis="x", linestyle=":", alpha=0.35)

    present_groups = guideline_df["Guideline Group"].drop_duplicates().tolist()
    handles = [Patch(facecolor=GUIDELINE_GROUP_COLORS[label], label=label) for label in group_order if label in present_groups]
    axes[1].legend(handles=handles, title="Guideline family", frameon=False, fontsize=8, title_fontsize=9, loc="lower right")

    plt.tight_layout()
    plt.savefig(f"{BASE}/figure_clinical_domain_and_guideline_distribution.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


def make_cross_model_error_heatmap(scores: pd.DataFrame, tax: pd.DataFrame):
    model_cols = [c for c in scores.columns if c not in ["Number", "RealAnswer"]]
    error_df = pd.DataFrame({"Number": scores["Number"]})
    for model in model_cols:
        error_df[model] = (
            scores[model].astype(str).str.strip() != scores["RealAnswer"].astype(str).str.strip()
        ).astype(int)

    merged = error_df.merge(
        tax[["Q No", "Main Domain"]].rename(columns={"Q No": "Number"}),
        on="Number",
        how="left",
    )
    merged["Main Domain"] = merged["Main Domain"].astype(str).str.strip()
    domain_counts = merged["Main Domain"].value_counts()
    keep_domains = domain_counts[domain_counts >= 3].index.tolist()
    merged["Domain_Grouped"] = merged["Main Domain"].where(merged["Main Domain"].isin(keep_domains), "Other")

    heat = merged.groupby("Domain_Grouped")[model_cols].mean()
    order_domains = merged["Domain_Grouped"].value_counts().index.tolist()
    heat = heat.reindex(order_domains)

    # sort models by family then by accuracy descending
    acc = {}
    for model in model_cols:
        acc[model] = 1 - error_df[model].mean()
    model_order = sorted(
        model_cols,
        key=lambda m: (FAMILY_MAP.get(standardize_model_label(m), "Other"), -acc[m], m),
    )
    heat = heat[model_order]
    standardized_order = standardize_model_labels(model_order)
    heat.columns = standardized_order
    heat.to_csv(f"{BASE}/cross_model_error_by_main_domain.csv")

    cmap = LinearSegmentedColormap.from_list(
        "error_heat",
        ["#f7fbff", "#c6dbef", "#6baed6", "#2171b5", "#08306b"],
        N=256,
    )
    vmax = float(np.nanmax(heat.values))
    vmax = max(0.35, min(1.0, vmax))
    fig, ax = plt.subplots(figsize=(14, 8))
    im = ax.imshow(heat.values, aspect="auto", cmap=cmap, vmin=0, vmax=vmax)
    ax.set_xticks(np.arange(len(standardized_order)))
    ax.set_xticklabels(standardized_order, rotation=55, ha="right", fontsize=8)
    ax.set_yticks(np.arange(len(heat.index)))
    ax.set_yticklabels(heat.index, fontsize=9)
    ax.set_xlabel("Language Models")
    ax.set_ylabel("Main Domain")

    cbar = fig.colorbar(im, ax=ax, fraction=0.025, pad=0.02)
    cbar.ax.tick_params(labelsize=8)

    # family color strip
    y_top = -0.95
    for i, model in enumerate(standardized_order):
        fam = FAMILY_MAP.get(model, "Other")
        ax.add_patch(Rectangle((i - 0.5, y_top), 1.0, 0.25, color=FAMILY_COLORS.get(fam, "#333333"), transform=ax.transData, clip_on=False))

    family_handles = [Patch(facecolor=color, label=family) for family, color in FAMILY_COLORS.items() if family in [FAMILY_MAP.get(m, "Other") for m in standardized_order]]
    ax.legend(
        handles=family_handles,
        title="LLM family",
        frameon=False,
        loc="upper left",
        bbox_to_anchor=(1.16, 1.0),
        fontsize=8,
        title_fontsize=9,
        borderaxespad=0.0,
    )

    plt.tight_layout()
    plt.savefig(f"{BASE}/figure_cross_model_error_patterns_main_domains.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


def main():
    scores, tax = load_data()
    make_content_distribution_figure(tax)
    make_cross_model_error_heatmap(scores, tax)
    make_question_level_correctness_plot(scores, tax)
    make_filtered_question_level_correctness_plots(scores, tax)
    print(f"Saved {BASE}/figure_clinical_domain_and_guideline_distribution.png")
    print(f"Saved {BASE}/figure_cross_model_error_patterns_main_domains.png")
    print(f"Saved {BASE}/figure_question_level_correctness_matrix.png")
    print(f"Saved {BASE}/figure_question_level_incorrect_at_least_1.png")
    print(f"Saved {BASE}/figure_question_level_incorrect_at_least_10.png")


def make_question_level_correctness_plot(scores: pd.DataFrame, tax: pd.DataFrame):
    model_cols = [c for c in scores.columns if c not in ["Number", "RealAnswer"]]
    standardized_models = standardize_model_labels(model_cols)
    columns = {}
    labels = []
    for _, row in scores.iterrows():
        qnum = int(row["Number"])
        dom = tax.loc[tax["Q No"] == qnum, "Main Domain"].astype(str).str.strip().iloc[0]
        sub = tax.loc[tax["Q No"] == qnum, "Subdomain"].astype(str).str.strip().iloc[0]
        label = f"Q{qnum}: {dom} | {sub}"
        labels.append(label)
        columns[label] = [
            int(str(row[m]).strip() == str(row["RealAnswer"]).strip()) for m in model_cols
        ]

    correctness = pd.DataFrame(columns, index=standardized_models)
    correctness.to_csv(f"{BASE}/question_level_correctness_matrix.csv")

    fig, ax = plt.subplots(figsize=(24, 7))
    cmap = plt.matplotlib.colors.ListedColormap(["#1f77b4", "#f0f0f0"])
    ax.imshow(correctness.values, aspect="auto", cmap=cmap, vmin=0, vmax=1)
    ax.set_yticks(range(len(standardized_models)))
    ax.set_yticklabels(standardized_models, fontsize=8)
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=60, ha="right", fontsize=6)
    ax.set_xlabel("Questions (Main Domain | Subdomain)")
    ax.set_ylabel("Language Models")

    legend_handles = [
        Patch(facecolor="#f0f0f0", edgecolor="#cccccc", label="Correct"),
        Patch(facecolor="#1f77b4", label="Incorrect"),
    ]
    ax.legend(
        handles=legend_handles,
        frameon=False,
        loc="upper left",
        bbox_to_anchor=(1.01, 1.0),
        fontsize=8,
        borderaxespad=0.0,
    )

    # light grid
    ax.set_xticks(np.arange(-0.5, len(labels), 1), minor=True)
    ax.set_yticks(np.arange(-0.5, len(model_cols), 1), minor=True)
    ax.grid(which="minor", color="white", linestyle="-", linewidth=0.5)
    ax.tick_params(which="minor", bottom=False, left=False)

    plt.tight_layout()
    plt.savefig(f"{BASE}/figure_question_level_correctness_matrix.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


def _build_correctness_matrix(scores: pd.DataFrame, tax: pd.DataFrame):
    model_cols = [c for c in scores.columns if c not in ["Number", "RealAnswer"]]
    columns = {}
    incorrect_counts = []
    for _, row in scores.iterrows():
        qnum = int(row["Number"])
        dom = tax.loc[tax["Q No"] == qnum, "Main Domain"].astype(str).str.strip().iloc[0]
        sub = tax.loc[tax["Q No"] == qnum, "Subdomain"].astype(str).str.strip().iloc[0]
        vals = [int(str(row[m]).strip() == str(row["RealAnswer"]).strip()) for m in model_cols]
        label = f"Q{qnum}: {dom} | {sub}"
        incorrect_counts.append(len(vals) - sum(vals))
        columns[label] = vals
    correctness = pd.DataFrame(columns, index=standardize_model_labels(model_cols))
    return correctness, incorrect_counts


def _draw_correctness_matrix(df: pd.DataFrame, output_path: str):
    fig_w = max(12, 0.18 * len(df.columns))
    fig, ax = plt.subplots(figsize=(fig_w, 7))
    cmap = plt.matplotlib.colors.ListedColormap(["#1f77b4", "#f0f0f0"])
    ax.imshow(df.values, aspect="auto", cmap=cmap, vmin=0, vmax=1)
    ax.set_yticks(range(len(df.index)))
    ax.set_yticklabels(df.index, fontsize=8)
    ax.set_xticks(range(len(df.columns)))
    ax.set_xticklabels(df.columns, rotation=60, ha="right", fontsize=6)
    ax.set_xlabel("Questions (Main Domain | Subdomain)")
    ax.set_ylabel("Language Models")

    legend_handles = [
        Patch(facecolor="#f0f0f0", edgecolor="#cccccc", label="Correct"),
        Patch(facecolor="#1f77b4", label="Incorrect"),
    ]
    ax.legend(
        handles=legend_handles,
        frameon=False,
        loc="upper left",
        bbox_to_anchor=(1.01, 1.0),
        fontsize=8,
        borderaxespad=0.0,
    )

    ax.set_xticks(np.arange(-0.5, len(df.columns), 1), minor=True)
    ax.set_yticks(np.arange(-0.5, len(df.index), 1), minor=True)
    ax.grid(which="minor", color="white", linestyle="-", linewidth=0.5)
    ax.tick_params(which="minor", bottom=False, left=False)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)


def make_filtered_question_level_correctness_plots(scores: pd.DataFrame, tax: pd.DataFrame):
    correctness, incorrect_counts = _build_correctness_matrix(scores, tax)
    counts = pd.Series(incorrect_counts, index=correctness.columns)

    at_least_1 = correctness.loc[:, counts >= 1]
    at_least_10 = correctness.loc[:, counts >= 10]

    at_least_1.to_csv(f"{BASE}/question_level_incorrect_at_least_1.csv")
    at_least_10.to_csv(f"{BASE}/question_level_incorrect_at_least_10.csv")

    _draw_correctness_matrix(at_least_1, f"{BASE}/figure_question_level_incorrect_at_least_1.png")
    _draw_correctness_matrix(at_least_10, f"{BASE}/figure_question_level_incorrect_at_least_10.png")


if __name__ == "__main__":
    main()
