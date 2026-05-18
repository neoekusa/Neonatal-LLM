import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.api as sm
import statsmodels.formula.api as smf
from _paths import OUTPUTS_DIR, RAW_SCORES, RAW_TAXONOMY

BASE = str(OUTPUTS_DIR)
SCORES = str(RAW_SCORES)
TAXONOMY = str(RAW_TAXONOMY)


def p_fmt(value):
    if value < 0.001:
        return "p<0.001"
    return f"p={value:.3f}"


def pretty_label(term: str) -> str:
    label_map = {
        "C(Knowledge, Treatment(reference='Factual'))[T.Conceptual]": "Knowledge dimension: Conceptual vs Factual",
        "C(Knowledge, Treatment(reference='Factual'))[T.Metacognitive]": "Knowledge dimension: Metacognitive vs Factual",
        "C(Knowledge, Treatment(reference='Factual'))[T.Procedural]": "Knowledge dimension: Procedural vs Factual",
        "C(Cognitive, Treatment(reference='Remember'))[T.Analyze]": "Cognitive process: Analyze vs Remember",
        "C(Cognitive, Treatment(reference='Remember'))[T.Apply]": "Cognitive process: Apply vs Remember",
        "C(Cognitive, Treatment(reference='Remember'))[T.Evaluate]": "Cognitive process: Evaluate vs Remember",
        "C(Cognitive, Treatment(reference='Remember'))[T.Understand]": "Cognitive process: Understand vs Remember",
        "C(Complexity, Treatment(reference='Low'))[T.High]": "Reasoning complexity: High vs Low",
        "C(Complexity, Treatment(reference='Low'))[T.Moderate]": "Reasoning complexity: Moderate vs Low",
        "C(Risk, Treatment(reference='Low'))[T.Medium]": "Clinical risk: Medium vs Low",
        "C(Risk, Treatment(reference='Low'))[T.High]": "Clinical risk: High vs Low",
        "C(Risk, Treatment(reference='Low'))[T.Critical]": "Clinical risk: Critical vs Low",
        "C(Difficulty, Treatment(reference='Low'))[T.Medium]": "Difficulty: Medium vs Low",
        "C(Difficulty, Treatment(reference='Low'))[T.Hard]": "Difficulty: Hard vs Low",
        "C(Task, Treatment(reference='1_Physiology_and_Pathophysiology'))[T.2_Epidemiology_and_Risk_Assessment]": "Task category: Epidemiology and risk assessment vs Physiology and pathophysiology",
        "C(Task, Treatment(reference='1_Physiology_and_Pathophysiology'))[T.3_Diagnosis]": "Task category: Diagnosis vs Physiology and pathophysiology",
        "C(Task, Treatment(reference='1_Physiology_and_Pathophysiology'))[T.4_Management_and_Treatment]": "Task category: Management and treatment vs Physiology and pathophysiology",
    }
    return label_map.get(term, term)


def main():
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
        C(Knowledge, Treatment(reference='Factual')) +
        C(Cognitive, Treatment(reference='Remember')) +
        C(Complexity, Treatment(reference='Low')) +
        C(Risk, Treatment(reference='Low')) +
        C(Difficulty, Treatment(reference='Low')) +
        C(Task, Treatment(reference='1_Physiology_and_Pathophysiology'))"""

    gee = smf.gee(
        formula,
        groups=df["Number"],
        data=df,
        family=sm.families.Binomial(),
        cov_struct=sm.cov_struct.Exchangeable(),
    ).fit()

    conf = gee.conf_int()
    results = pd.DataFrame(
        {
            "term": gee.params.index,
            "coef_log_odds": gee.params.values,
            "se": gee.bse.values,
            "z": gee.tvalues.values,
            "p_value": gee.pvalues.values,
            "ci_low_logodds": conf[0].values,
            "ci_high_logodds": conf[1].values,
        }
    )
    results["odds_ratio"] = np.exp(results["coef_log_odds"])
    results["ci_low"] = np.exp(results["ci_low_logodds"])
    results["ci_high"] = np.exp(results["ci_high_logodds"])
    results["aOR_95_CI"] = results.apply(
        lambda r: f"[{r['ci_low']:.2f}, {r['ci_high']:.2f}]",
        axis=1,
    )
    results.to_csv(f"{BASE}/full_exploratory_remember_results.csv", index=False)

    display = results.copy()
    display = display[display["term"] != "Intercept"].copy()
    display.to_csv(f"{BASE}/TableS1_Expanded_Exploratory_GEE.csv", index=False)

    qic_out = gee.model.qic(gee.params, scale=1.0, cov_params=gee.cov_params())
    qic = float(qic_out[1])
    qicu = float(qic_out[2])
    pd.DataFrame([{"QIC": qic, "QICu": qicu}]).to_csv(
        f"{BASE}/full_exploratory_remember_qic_qicu.csv", index=False
    )

    plot_df = display.copy()
    plot_df["plot_or"] = plot_df["odds_ratio"].clip(lower=1e-3, upper=1e3)
    plot_df["plot_low"] = plot_df["ci_low"].clip(lower=1e-3, upper=1e3)
    plot_df["plot_high"] = plot_df["ci_high"].replace([np.inf, -np.inf], np.nan).fillna(1e3).clip(lower=1e-3, upper=1e3)
    plot_df = plot_df.sort_values("plot_or")
    fig, ax = plt.subplots(figsize=(11, 8))
    y = np.arange(len(plot_df))
    colors = ["#b22222" if p < 0.05 else "#333333" for p in plot_df["p_value"]]

    ax.errorbar(
        plot_df["plot_or"],
        y,
        xerr=[
            plot_df["plot_or"] - plot_df["plot_low"],
            plot_df["plot_high"] - plot_df["plot_or"],
        ],
        fmt="o",
        color="#333333",
        ecolor="#999999",
        elinewidth=1.1,
        capsize=3.5,
        markersize=4.8,
    )
    for yi, (_, row), color in zip(y, plot_df.iterrows(), colors):
        ax.scatter(row["plot_or"], yi, color=color, s=24, zorder=3)
        ax.text(
            min(row["plot_high"] * 1.08, 1200),
            yi,
            f"OR {row['odds_ratio']:.2f}; {p_fmt(row['p_value'])}",
            va="center",
            fontsize=8,
            color=color,
        )

    ax.set_yticks(y)
    ax.set_yticklabels(plot_df["term"].map(pretty_label), fontsize=8)
    ax.axvline(1, color="#1f4e79", linestyle="--", linewidth=1)
    ax.set_xscale("log")
    ax.set_xlabel("Adjusted Odds Ratio for Error (95% CI)")
    ax.set_xlim(1e-3, 1e3)
    ax.grid(axis="x", linestyle=":", alpha=0.45)
    plt.tight_layout()
    plt.savefig(f"{BASE}/full_exploratory_remember_forest.png", dpi=300, bbox_inches="tight")
    plt.close(fig)

    # Clean QIC comparison table for supplement
    qic_all = pd.read_csv(f"{BASE}/all_model_qic_qicu_comparison.csv")
    qic_clean = qic_all[~qic_all["model_spec"].str.contains("apply_reference")].copy()
    qic_clean.to_csv(f"{BASE}/TableS4_QIC_QICu_Model_Comparison.csv", index=False)

    reference_check_path = f"{BASE}/full_model_reference_qic_check.csv"
    try:
        ref_check = pd.read_csv(reference_check_path)
        ref_check = ref_check.rename(
            columns={
                "qic": "QIC",
                "qicu": "QICu",
                "not_qic_quasi_likelihood": "Not_QIC_Quasi_Likelihood",
            }
        )
    except FileNotFoundError:
        ref_check = pd.DataFrame(
            [
                {
                    "spec": "full_taxonomy_remember_reference",
                    "QIC": qic,
                    "QICu": qicu,
                    "Not_QIC_Quasi_Likelihood": "",
                    "note": "Final expanded-model parameterization.",
                    "interpretation": (
                        "Run compare_all_model_qic.py before this script for the full "
                        "reference-coding diagnostic."
                    ),
                },
            ]
        )
    ref_check.to_csv(f"{BASE}/TableS5_Reference_Coding_QIC_Check.csv", index=False)

    print(f"Saved {BASE}/TableS1_Expanded_Exploratory_GEE.csv")
    print(f"Saved {BASE}/full_exploratory_remember_results.csv")
    print(f"Saved {BASE}/full_exploratory_remember_qic_qicu.csv")
    print(f"Saved {BASE}/full_exploratory_remember_forest.png")
    print(f"Saved {BASE}/TableS4_QIC_QICu_Model_Comparison.csv")
    print(f"Saved {BASE}/TableS5_Reference_Coding_QIC_Check.csv")


if __name__ == "__main__":
    main()
