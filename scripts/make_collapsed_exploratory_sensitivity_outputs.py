import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.api as sm
import statsmodels.formula.api as smf
from scipy.stats import chi2 as chi2dist
from _paths import OUTPUTS_DIR, RAW_SCORES, RAW_TAXONOMY

BASE = str(OUTPUTS_DIR)
SCORES = str(RAW_SCORES)
TAXONOMY = str(RAW_TAXONOMY)


LABEL_MAP = {
    "C(Knowledge_collapsed, Treatment(reference='Factual'))[T.Conceptual]": "Knowledge dimension: Conceptual/Metacognitive vs Factual",
    "C(Knowledge_collapsed, Treatment(reference='Factual'))[T.Procedural]": "Knowledge dimension: Procedural vs Factual",
    "C(Cognitive_collapsed, Treatment(reference='Remember'))[T.Analyze]": "Cognitive process: Analyze/Evaluate vs Remember",
    "C(Cognitive_collapsed, Treatment(reference='Remember'))[T.Apply]": "Cognitive process: Apply vs Remember",
    "C(Cognitive_collapsed, Treatment(reference='Remember'))[T.Understand]": "Cognitive process: Understand vs Remember",
    "C(Complexity, Treatment(reference='Low'))[T.High]": "Reasoning complexity: High vs Low",
    "C(Complexity, Treatment(reference='Low'))[T.Moderate]": "Reasoning complexity: Moderate vs Low",
    "C(Risk, Treatment(reference='Low'))[T.Critical]": "Clinical risk: Critical vs Low",
    "C(Risk, Treatment(reference='Low'))[T.High]": "Clinical risk: High vs Low",
    "C(Risk, Treatment(reference='Low'))[T.Medium]": "Clinical risk: Medium vs Low",
    "C(Risk, Treatment(reference='Low'))[T.Nan]": "Clinical risk: Missing vs Low",
    "C(Difficulty, Treatment(reference='Low'))[T.Hard]": "Difficulty: Hard vs Low",
    "C(Difficulty, Treatment(reference='Low'))[T.Medium]": "Difficulty: Medium vs Low",
    "C(Task, Treatment(reference='1_Physiology_and_Pathophysiology'))[T.2_Epidemiology_and_Risk_Assessment]": "Task category: Epidemiology and risk assessment vs Physiology and pathophysiology",
    "C(Task, Treatment(reference='1_Physiology_and_Pathophysiology'))[T.3_Diagnosis]": "Task category: Diagnosis vs Physiology and pathophysiology",
    "C(Task, Treatment(reference='1_Physiology_and_Pathophysiology'))[T.4_Management_and_Treatment]": "Task category: Management and treatment vs Physiology and pathophysiology",
}


def p_fmt(value):
    return "p<0.001" if value < 0.001 else f"p={value:.3f}"


def load_data():
    scores = pd.read_csv(SCORES)
    tax = pd.read_csv(TAXONOMY)
    scores.columns = [c.strip() for c in scores.columns]
    tax.columns = [c.strip() for c in tax.columns]

    model_cols = [c for c in scores.columns if c not in ["Number", "RealAnswer"]]
    df_long = scores.melt(
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

    tax_clean = tax.rename(
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

    df["Knowledge_collapsed"] = df["Knowledge"].replace({"Metacognitive": "Conceptual"})
    df["Cognitive_collapsed"] = df["Cognitive"].replace({"Evaluate": "Analyze"})
    return df


def fit_model(df):
    formula = """Failure ~
        C(Knowledge_collapsed, Treatment(reference='Factual')) +
        C(Cognitive_collapsed, Treatment(reference='Remember')) +
        C(Complexity, Treatment(reference='Low')) +
        C(Risk, Treatment(reference='Low')) +
        C(Difficulty, Treatment(reference='Low')) +
        C(Task, Treatment(reference='1_Physiology_and_Pathophysiology'))"""
    return smf.gee(
        formula,
        groups=df["Number"],
        data=df,
        family=sm.families.Binomial(),
        cov_struct=sm.cov_struct.Exchangeable(),
    ).fit()


def save_results(res):
    conf = res.conf_int()
    out = pd.DataFrame(
        {
            "term": res.params.index,
            "coef_log_odds": res.params.values,
            "se": res.bse.values,
            "z": res.tvalues.values,
            "p_value": res.pvalues.values,
            "ci_low_logodds": conf[0].values,
            "ci_high_logodds": conf[1].values,
        }
    )
    out["odds_ratio"] = np.exp(out["coef_log_odds"])
    out["ci_low"] = np.exp(out["ci_low_logodds"])
    out["ci_high"] = np.exp(out["ci_high_logodds"])
    out["label"] = out["term"].map(LABEL_MAP).fillna(out["term"])
    out.to_csv(f"{BASE}/exploratory_collapsed_meta_eval_results.csv", index=False)
    return out


def save_wald(res):
    factors = {
        "Knowledge dimension (collapsed)": [i for i, t in enumerate(res.params.index) if "Knowledge_collapsed" in t],
        "Cognitive process (collapsed)": [i for i, t in enumerate(res.params.index) if "Cognitive_collapsed" in t],
        "Reasoning complexity": [i for i, t in enumerate(res.params.index) if "Complexity" in t],
        "Clinical risk": [i for i, t in enumerate(res.params.index) if "Risk" in t],
        "Difficulty": [i for i, t in enumerate(res.params.index) if "Difficulty" in t],
        "Universal task category": [i for i, t in enumerate(res.params.index) if "Task" in t],
    }

    rows = []
    cov = res.cov_params().values
    params = res.params.values
    for factor, idx in factors.items():
        b = params[idx]
        V = cov[np.ix_(idx, idx)]
        chi2 = float(b @ np.linalg.pinv(V) @ b)
        df_num = len(idx)
        pval = float(1 - chi2dist.cdf(chi2, df_num))
        rows.append({"factor": factor, "wald_chi2": chi2, "df": df_num, "p_value": pval})

    out = pd.DataFrame(rows)
    out["p_value_fmt"] = out["p_value"].map(lambda x: "<0.001" if x < 0.001 else f"{x:.3f}")
    out.to_csv(f"{BASE}/exploratory_collapsed_meta_eval_wald.csv", index=False)
    out.to_csv(f"{BASE}/TableS6_Collapsed_Exploratory_Wald.csv", index=False)
    return out


def make_forest(results):
    plot_df = results[results["term"] != "Intercept"].copy()
    plot_df["plot_or"] = plot_df["odds_ratio"].clip(lower=1e-3, upper=1e3)
    plot_df["plot_low"] = plot_df["ci_low"].clip(lower=1e-3, upper=1e3)
    plot_df["plot_high"] = (
        plot_df["ci_high"]
        .replace([np.inf, -np.inf], np.nan)
        .fillna(1e3)
        .clip(lower=1e-3, upper=1e3)
    )
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
    ax.set_yticklabels(plot_df["label"], fontsize=7)
    ax.axvline(1, color="#1f4e79", linestyle="--", linewidth=1)
    ax.set_xscale("log")
    ax.set_xlabel("Adjusted Odds Ratio for Error (95% CI)")
    ax.set_xlim(1e-3, 1e3)
    ax.grid(axis="x", linestyle=":", alpha=0.45)
    plt.tight_layout()
    plt.savefig(f"{BASE}/full_exploratory_collapsed_forest_publication.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


def save_qic(res):
    qic_out = res.model.qic(res.params, scale=1.0, cov_params=res.cov_params())
    qic = float(qic_out[1]) if len(qic_out) >= 3 else float(qic_out[0])
    qicu = float(qic_out[2]) if len(qic_out) >= 3 else float(qic_out[1])
    pd.DataFrame(
        [{"model": "collapsed_exploratory_sensitivity", "QIC": qic, "QICu": qicu}]
    ).to_csv(f"{BASE}/collapsed_exploratory_qic_qicu.csv", index=False)


def main():
    df = load_data()
    res = fit_model(df)
    results = save_results(res)
    save_wald(res)
    make_forest(results)
    save_qic(res)
    print(f"Saved {BASE}/full_exploratory_collapsed_forest_publication.png")
    print(f"Saved {BASE}/TableS6_Collapsed_Exploratory_Wald.csv")


if __name__ == "__main__":
    main()
