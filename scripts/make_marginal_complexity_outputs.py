import matplotlib
matplotlib.use("Agg")
import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.api as sm
import statsmodels.formula.api as smf

from _paths import OUTPUTS_DIR, RAW_SCORES, RAW_TAXONOMY


BASE = str(OUTPUTS_DIR)


def load_analysis_df():
    scores_df = pd.read_csv(RAW_SCORES)
    tax_df = pd.read_csv(RAW_TAXONOMY)

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
    return df


def fit_primary_model(df):
    formula = """Failure ~
        C(Cognitive, Treatment(reference='Remember')) +
        C(Complexity, Treatment(reference='Low')) +
        C(Task, Treatment(reference='1_Physiology_and_Pathophysiology'))"""

    return smf.gee(
        formula,
        groups=df["Number"],
        data=df,
        family=sm.families.Binomial(),
        cov_struct=sm.cov_struct.Exchangeable(),
    ).fit()


def average_marginal_predictions(fit, df):
    rows = []
    for level in ["Low", "Moderate", "High"]:
        counterfactual = df.copy()
        counterfactual["Complexity"] = level
        prob = float(fit.predict(counterfactual).mean())
        rows.append(
            {
                "Reasoning_Complexity": level,
                "Predicted_Failure_Probability": prob,
            }
        )

    out = pd.DataFrame(rows)
    out["Predicted_Success_Probability"] = 1 - out["Predicted_Failure_Probability"]
    low = out.loc[
        out["Reasoning_Complexity"] == "Low", "Predicted_Failure_Probability"
    ].iloc[0]
    out["Absolute_Increase_vs_Low"] = out["Predicted_Failure_Probability"] - low
    out["Failure_Percent"] = 100 * out["Predicted_Failure_Probability"]
    out["Success_Percent"] = 100 * out["Predicted_Success_Probability"]
    out["Absolute_Increase_vs_Low_PercentPoints"] = 100 * out["Absolute_Increase_vs_Low"]
    return out


def save_outputs(df):
    df.to_csv(f"{BASE}/TableS9_Marginal_Predicted_Failure_By_Complexity.csv", index=False)

    fig, ax = plt.subplots(figsize=(7.4, 5.4))
    colors = ["#4F7DE0", "#F4B400", "#E66A4C"]
    bars = ax.bar(
        df["Reasoning_Complexity"],
        df["Failure_Percent"],
        color=colors,
        edgecolor="#2F3640",
        linewidth=1.1,
        width=0.62,
    )

    for i, (bar, yi) in enumerate(zip(bars, df["Failure_Percent"])):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            yi + 0.9,
            f"{yi:.1f}%",
            ha="center",
            va="bottom",
            fontsize=11,
            fontweight="bold",
            color="#1F2933",
        )

    ax.set_ylabel("Predicted Failure Probability (%)")
    ax.set_xlabel("Reasoning Complexity")
    ax.set_ylim(0, max(df["Failure_Percent"]) + 6)
    ax.grid(axis="y", linestyle=":", alpha=0.4)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    plt.tight_layout()
    plt.savefig(f"{BASE}/graph_marginal_failure_by_complexity.png", dpi=300, bbox_inches="tight")
    plt.close(fig)

    with open(f"{BASE}/marginal_complexity_summary.txt", "w", encoding="utf-8") as fh:
        fh.write(
            "Average marginal predicted failure probabilities from the primary clustered GEE model\n"
            "For each reasoning-complexity level, predictions were generated after setting all observations\n"
            "to that complexity level while retaining the observed distribution of the other covariates.\n"
            f"Low: {df.loc[0, 'Failure_Percent']:.1f}%\n"
            f"Moderate: {df.loc[1, 'Failure_Percent']:.1f}% "
            f"(absolute increase vs low: {df.loc[1, 'Absolute_Increase_vs_Low_PercentPoints']:.1f} percentage points)\n"
            f"High: {df.loc[2, 'Failure_Percent']:.1f}% "
            f"(absolute increase vs low: {df.loc[2, 'Absolute_Increase_vs_Low_PercentPoints']:.1f} percentage points)\n"
        )


def main():
    df = load_analysis_df()
    fit = fit_primary_model(df)
    margins = average_marginal_predictions(fit, df)
    save_outputs(margins)
    print(margins.to_string(index=False))
    print(f"\nSaved {BASE}/TableS9_Marginal_Predicted_Failure_By_Complexity.csv")
    print(f"Saved {BASE}/graph_marginal_failure_by_complexity.png")
    print(f"Saved {BASE}/marginal_complexity_summary.txt")


if __name__ == "__main__":
    main()
