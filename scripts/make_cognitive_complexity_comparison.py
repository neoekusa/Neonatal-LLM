import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.api as sm
import statsmodels.formula.api as smf
from _paths import OUTPUTS_DIR, RAW_SCORES, RAW_TAXONOMY

BASE = str(OUTPUTS_DIR)
SCORES = str(RAW_SCORES)
TAXONOMY = str(RAW_TAXONOMY)


def p_fmt(value: float) -> str:
    if pd.isna(value):
        return ""
    if value < 0.001:
        return "p<0.001"
    return f"p={value:.3f}"


def scalar(value):
    if isinstance(value, (list, tuple, np.ndarray)):
        return float(np.asarray(value).reshape(-1)[0])
    return float(value)


def load_new_model_outputs():
    coeff = pd.read_csv(f"{BASE}/clean_gee_results.csv")
    qic = pd.read_csv(f"{BASE}/clean_gee_qic_qicu.csv").iloc[0]
    return coeff, qic


def run_new_model_wald():
    scores_df = pd.read_csv(SCORES)
    tax_df = pd.read_csv(TAXONOMY)
    scores_df.columns = [c.strip() for c in scores_df.columns]
    tax_df.columns = [c.strip() for c in tax_df.columns]

    model_cols = [c for c in scores_df.columns if c not in ["Number", "RealAnswer"]]
    df_long = scores_df.melt(
        id_vars=["Number", "RealAnswer"],
        value_vars=model_cols,
        var_name="Model",
        value_name="Answer",
    )
    df_long["Failure"] = (
        ~df_long["Answer"].astype(str).str.strip().eq(
            df_long["RealAnswer"].astype(str).str.strip()
        )
    ).astype(int)

    tax_clean = tax_df.rename(
        columns={
            "Q No": "Q_No",
            "Knowledge Dimension": "Knowledge",
            "Cognitive Process": "Cognitive",
            "Reasoning  Complexity": "Complexity",
            "Clinical Risk": "Risk",
            "Difficulty": "Difficulty",
            "Universal Task Category": "Task",
        }
    )
    df = pd.merge(df_long, tax_clean, left_on="Number", right_on="Q_No")

    for col in ["Knowledge", "Cognitive", "Complexity", "Risk", "Difficulty", "Task"]:
        df[col] = (
            df[col]
            .astype(str)
            .str.strip()
            .str.replace(" ", "_", regex=False)
            .str.replace(".", "", regex=False)
            .str.replace("/", "_", regex=False)
        )

    formula = """Failure ~
        C(Cognitive, Treatment(reference='Remember')) +
        C(Complexity, Treatment(reference='Low'))"""

    gee = smf.gee(
        formula,
        groups=df["Number"],
        data=df,
        family=sm.families.Binomial(),
        cov_struct=sm.cov_struct.Exchangeable(),
    ).fit()

    wald = gee.wald_test_terms().summary_frame().reset_index()
    wald = wald.rename(columns={"index": "factor", "chi2": "wald_chi2", "P>chi2": "p_value", "df constraint": "df_constraint"})
    keep = ["C(Cognitive, Treatment(reference='Remember'))", "C(Complexity, Treatment(reference='Low'))"]
    wald = wald[wald["factor"].isin(keep)].copy()
    wald["factor"] = wald["factor"].map(
        {
            "C(Cognitive, Treatment(reference='Remember'))": "Cognitive_Process",
            "C(Complexity, Treatment(reference='Low'))": "Reasoning_Complexity",
        }
    )
    wald["df"] = wald["df_constraint"].astype(int)
    return wald[["factor", "wald_chi2", "df", "p_value"]]


def build_comparison_table(old_coeff: pd.DataFrame, old_wald: pd.DataFrame, new_coeff: pd.DataFrame, new_wald: pd.DataFrame, new_qic: pd.Series):
    rows = []

    def pull_term(df, *contains_options):
        term_series = df["term"].astype(str)
        for contains in contains_options:
            subset = df[term_series.str.contains(contains, regex=False)]
            if not subset.empty:
                return subset.iloc[0]
        raise KeyError(f"Could not find term matching any of: {contains_options}")

    old_mod = pull_term(
        old_coeff,
        'Reasoning_Complexity, Treatment(reference="Low"))[T.Moderate]',
        "C(Reasoning_Complexity, Treatment(reference='Low'))[T.Moderate]",
        "[T.Moderate]",
    )
    old_high = pull_term(
        old_coeff,
        'Reasoning_Complexity, Treatment(reference="Low"))[T.High]',
        "C(Reasoning_Complexity, Treatment(reference='Low'))[T.High]",
        "[T.High]",
    )
    new_mod = pull_term(new_coeff, "C(Complexity, Treatment(reference='Low'))[T.Moderate]")
    new_high = pull_term(new_coeff, "C(Complexity, Treatment(reference='Low'))[T.High]")
    old_apply = pull_term(
        old_coeff,
        'Cognitive_Process, Treatment(reference="Remember"))[T.Apply]',
        "C(Cognitive_Process, Treatment(reference='Remember'))[T.Apply]",
        "[T.Apply]",
    )
    new_apply = pull_term(new_coeff, "C(Cognitive, Treatment(reference='Remember'))[T.Apply]")

    old_qic = pd.read_csv(f"{BASE}/high_journal_primary_qic_qicu.csv").iloc[0]

    rows.extend([
        {
            "comparison_item": "Model specification",
            "previous_primary_model": "Cognitive + Complexity + Universal Task",
            "new_cognitive_complexity_model": "Cognitive + Complexity",
        },
        {
            "comparison_item": "Reasoning Complexity joint Wald",
            "previous_primary_model": f"chi2={old_wald.loc[old_wald['factor']=='Reasoning_Complexity','wald_chi2'].iloc[0]:.2f}, p={old_wald.loc[old_wald['factor']=='Reasoning_Complexity','p_value'].iloc[0]:.3f}",
            "new_cognitive_complexity_model": f"chi2={scalar(new_wald.loc[new_wald['factor']=='Reasoning_Complexity','wald_chi2'].iloc[0]):.2f}, p={scalar(new_wald.loc[new_wald['factor']=='Reasoning_Complexity','p_value'].iloc[0]):.3f}",
        },
        {
            "comparison_item": "Cognitive Process joint Wald",
            "previous_primary_model": f"chi2={old_wald.loc[old_wald['factor']=='Cognitive_Process','wald_chi2'].iloc[0]:.2f}, p={old_wald.loc[old_wald['factor']=='Cognitive_Process','p_value'].iloc[0]:.3f}",
            "new_cognitive_complexity_model": f"chi2={scalar(new_wald.loc[new_wald['factor']=='Cognitive_Process','wald_chi2'].iloc[0]):.2f}, p={scalar(new_wald.loc[new_wald['factor']=='Cognitive_Process','p_value'].iloc[0]):.3f}",
        },
        {
            "comparison_item": "Moderate vs Low complexity",
            "previous_primary_model": f"OR={old_mod['odds_ratio']:.2f} [{old_mod['ci_low']:.2f}, {old_mod['ci_high']:.2f}], {p_fmt(old_mod['p_value'])}",
            "new_cognitive_complexity_model": f"OR={new_mod['aOR']:.2f} [{new_mod['Lower_95']:.2f}, {new_mod['Upper_95']:.2f}], {p_fmt(new_mod['p_value'])}",
        },
        {
            "comparison_item": "High vs Low complexity",
            "previous_primary_model": f"OR={old_high['odds_ratio']:.2f} [{old_high['ci_low']:.2f}, {old_high['ci_high']:.2f}], {p_fmt(old_high['p_value'])}",
            "new_cognitive_complexity_model": f"OR={new_high['aOR']:.2f} [{new_high['Lower_95']:.2f}, {new_high['Upper_95']:.2f}], {p_fmt(new_high['p_value'])}",
        },
        {
            "comparison_item": "Apply vs Remember",
            "previous_primary_model": f"OR={old_apply['odds_ratio']:.2f} [{old_apply['ci_low']:.2f}, {old_apply['ci_high']:.2f}], {p_fmt(old_apply['p_value'])}",
            "new_cognitive_complexity_model": f"OR={new_apply['aOR']:.2f} [{new_apply['Lower_95']:.2f}, {new_apply['Upper_95']:.2f}], {p_fmt(new_apply['p_value'])}",
        },
        {
            "comparison_item": "QIC",
            "previous_primary_model": f"{old_qic['qic']:.2f}",
            "new_cognitive_complexity_model": f"{new_qic['QIC']:.2f}",
        },
        {
            "comparison_item": "QICu",
            "previous_primary_model": f"{old_qic['qicu']:.2f}",
            "new_cognitive_complexity_model": f"{new_qic['QICu']:.2f}",
        },
    ])
    return pd.DataFrame(rows)


def build_forest_plot(new_coeff: pd.DataFrame):
    plot_df = new_coeff[new_coeff["term"] != "Intercept"].copy()
    label_map = {
        "C(Cognitive, Treatment(reference='Remember'))[T.Analyze]": "Cognitive process: Analyze vs Remember",
        "C(Cognitive, Treatment(reference='Remember'))[T.Apply]": "Cognitive process: Apply vs Remember",
        "C(Cognitive, Treatment(reference='Remember'))[T.Evaluate]": "Cognitive process: Evaluate vs Remember",
        "C(Cognitive, Treatment(reference='Remember'))[T.Understand]": "Cognitive process: Understand vs Remember",
        "C(Complexity, Treatment(reference='Low'))[T.High]": "Reasoning complexity: High vs Low",
        "C(Complexity, Treatment(reference='Low'))[T.Moderate]": "Reasoning complexity: Moderate vs Low",
    }
    plot_df["label"] = plot_df["term"].map(label_map)
    plot_df = plot_df.sort_values("aOR")

    fig, ax = plt.subplots(figsize=(10.5, 6.5))
    y = np.arange(len(plot_df))
    colors = ["#b22222" if p < 0.05 else "#333333" for p in plot_df["p_value"]]

    ax.errorbar(
        plot_df["aOR"],
        y,
        xerr=[
            plot_df["aOR"] - plot_df["Lower_95"],
            plot_df["Upper_95"] - plot_df["aOR"],
        ],
        fmt="o",
        color="#333333",
        ecolor="#9a9a9a",
        elinewidth=1.2,
        capsize=3.5,
        markersize=5,
    )

    for yi, (_, row), color in zip(y, plot_df.iterrows(), colors):
        ax.scatter(row["aOR"], yi, color=color, s=28, zorder=3)
        ax.text(
            row["Upper_95"] * 1.18,
            yi,
            f"OR {row['aOR']:.2f}; {p_fmt(row['p_value'])}",
            va="center",
            fontsize=9,
            color=color,
            fontweight="bold" if row["p_value"] < 0.05 else "normal",
        )

    ax.set_yticks(y)
    ax.set_yticklabels(plot_df["label"], fontsize=9)
    ax.axvline(1, color="#1f4e79", linestyle="--", linewidth=1)
    ax.set_xscale("log")
    ax.set_xlabel("Adjusted Odds Ratio for Error (95% CI)")
    ax.grid(axis="x", linestyle=":", alpha=0.5)
    plt.tight_layout()
    plt.savefig(f"{BASE}/forest_plot_cognitive_complexity_journal.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


def main():
    old_coeff = pd.read_csv(f"{BASE}/high_journal_primary_gee_coefficients.csv")
    old_wald = pd.read_csv(f"{BASE}/high_journal_primary_gee_wald.csv")
    new_coeff, new_qic = load_new_model_outputs()
    new_wald = run_new_model_wald()

    comparison = build_comparison_table(old_coeff, old_wald, new_coeff, new_wald, new_qic)
    comparison.to_csv(f"{BASE}/comparison_previous_vs_cognitive_complexity_model.csv", index=False)
    new_wald.to_csv(f"{BASE}/clean_gee_joint_wald.csv", index=False)

    build_forest_plot(new_coeff)

    summary = (
        "Previous primary model: Cognitive + Complexity + Universal Task\n"
        f"Reasoning Complexity joint Wald: chi2={old_wald.loc[old_wald['factor']=='Reasoning_Complexity','wald_chi2'].iloc[0]:.2f}, "
        f"p={old_wald.loc[old_wald['factor']=='Reasoning_Complexity','p_value'].iloc[0]:.3f}\n"
        f"Cognitive Process joint Wald: chi2={old_wald.loc[old_wald['factor']=='Cognitive_Process','wald_chi2'].iloc[0]:.2f}, "
        f"p={old_wald.loc[old_wald['factor']=='Cognitive_Process','p_value'].iloc[0]:.3f}\n\n"
        "New model: Cognitive + Complexity\n"
        f"Reasoning Complexity joint Wald: chi2={scalar(new_wald.loc[new_wald['factor']=='Reasoning_Complexity','wald_chi2'].iloc[0]):.2f}, "
        f"p={scalar(new_wald.loc[new_wald['factor']=='Reasoning_Complexity','p_value'].iloc[0]):.3f}\n"
        f"Cognitive Process joint Wald: chi2={scalar(new_wald.loc[new_wald['factor']=='Cognitive_Process','wald_chi2'].iloc[0]):.2f}, "
        f"p={scalar(new_wald.loc[new_wald['factor']=='Cognitive_Process','p_value'].iloc[0]):.3f}\n"
    )
    with open(f"{BASE}/comparison_previous_vs_cognitive_complexity_summary.txt", "w", encoding="utf-8") as fh:
        fh.write(summary)

    print(comparison.to_string(index=False))
    print("\nSaved:")
    print(f"{BASE}/comparison_previous_vs_cognitive_complexity_model.csv")
    print(f"{BASE}/clean_gee_joint_wald.csv")
    print(f"{BASE}/forest_plot_cognitive_complexity_journal.png")
    print(f"{BASE}/comparison_previous_vs_cognitive_complexity_summary.txt")


if __name__ == "__main__":
    main()
