import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from statsmodels.stats.outliers_influence import variance_inflation_factor
from _paths import OUTPUTS_DIR, RAW_SCORES, RAW_TAXONOMY

SCORES_PATH = str(RAW_SCORES)
TAX_PATH = str(RAW_TAXONOMY)
OUT_DIR = str(OUTPUTS_DIR)


def load_and_prepare():
    scores_df = pd.read_csv(SCORES_PATH)
    tax_df = pd.read_csv(TAX_PATH)

    scores_df.columns = [c.strip() for c in scores_df.columns]
    tax_df.columns = [c.strip() for c in tax_df.columns]

    model_cols = [c for c in scores_df.columns if c not in ["Number", "RealAnswer"]]

    df_long = scores_df.melt(
        id_vars=["Number", "RealAnswer"],
        value_vars=model_cols,
        var_name="Model",
        value_name="Answer",
    )
    df_long["Correct"] = (
        df_long["Answer"].astype(str).str.strip().eq(
            df_long["RealAnswer"].astype(str).str.strip()
        )
    ).astype(int)
    df_long["Failure"] = 1 - df_long["Correct"]

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


def calculate_vif(data, factors):
    x = pd.get_dummies(data[factors], drop_first=True).astype(float)
    vif_data = pd.DataFrame(
        {
            "Variable": x.columns,
            "VIF": [variance_inflation_factor(x.values, i) for i in range(x.shape[1])],
        }
    ).sort_values("VIF", ascending=False)
    return vif_data


def main():
    df = load_and_prepare()

    # Keep VIF aligned with the predictors actually used in the models.
    factors = ["Cognitive", "Complexity"]
    vif_df = calculate_vif(df, factors)
    vif_path = f"{OUT_DIR}/clean_gee_lpm_vif.csv"
    vif_df.to_csv(vif_path, index=False)

    gee_formula = """Failure ~
        C(Cognitive, Treatment(reference='Remember')) +
        C(Complexity, Treatment(reference='Low'))"""

    gee_model = smf.gee(
        gee_formula,
        groups=df["Number"],
        data=df,
        family=sm.families.Binomial(),
        cov_struct=sm.cov_struct.Exchangeable(),
    ).fit(scale=1.0)

    gee_res = pd.DataFrame(
        {
            "term": gee_model.params.index,
            "B": gee_model.params.values,
            "SE": gee_model.bse.values,
            "z": gee_model.tvalues.values,
            "p_value": gee_model.pvalues.values,
        }
    )
    gee_res["aOR"] = np.exp(gee_res["B"])
    gee_res["Lower_95"] = np.exp(gee_res["B"] - 1.96 * gee_res["SE"])
    gee_res["Upper_95"] = np.exp(gee_res["B"] + 1.96 * gee_res["SE"])
    gee_res["aOR_95_CI"] = gee_res.apply(
        lambda x: f"[{x['Lower_95']:.2f}, {x['Upper_95']:.2f}]",
        axis=1,
    )
    gee_path = f"{OUT_DIR}/clean_gee_results.csv"
    gee_res.to_csv(gee_path, index=False)

    qic, qicu = gee_model.qic(scale=1.0)
    qic_df = pd.DataFrame([{"QIC": float(qic), "QICu": float(qicu)}])
    qic_path = f"{OUT_DIR}/clean_gee_qic_qicu.csv"
    qic_df.to_csv(qic_path, index=False)

    lpm_formula = """Correct ~
        C(Cognitive, Treatment(reference='Remember')) +
        C(Complexity, Treatment(reference='Low'))"""

    lpm_model = smf.ols(lpm_formula, data=df).fit(
        cov_type="cluster",
        cov_kwds={"groups": df["Number"]},
    )
    lpm_res = pd.DataFrame(
        {
            "term": lpm_model.params.index,
            "B": lpm_model.params.values,
            "SE": lpm_model.bse.values,
            "t": lpm_model.tvalues.values,
            "p_value": lpm_model.pvalues.values,
            "Lower_95": lpm_model.conf_int()[0].values,
            "Upper_95": lpm_model.conf_int()[1].values,
        }
    )
    lpm_path = f"{OUT_DIR}/clean_lpm_results.csv"
    lpm_res.to_csv(lpm_path, index=False)

    summary_path = f"{OUT_DIR}/clean_gee_lpm_summary.txt"
    with open(summary_path, "w") as f:
        f.write("=== VIF ===\n")
        f.write(vif_df.to_string(index=False))
        f.write("\n\n=== GEE SUMMARY ===\n")
        f.write(str(gee_model.summary()))
        f.write("\n\n=== LPM SUMMARY ===\n")
        f.write(str(lpm_model.summary()))

    print("VIF:")
    print(vif_df.to_string(index=False))
    print("\nGEE results:")
    print(gee_res[["term", "aOR", "p_value", "aOR_95_CI"]].to_string(index=False))
    print("\nQIC/QICu:")
    print(qic_df.to_string(index=False))
    print("\nLPM results:")
    print(lpm_res[["term", "B", "p_value", "Lower_95", "Upper_95"]].to_string(index=False))
    print("\nSaved files:")
    for path in [vif_path, gee_path, qic_path, lpm_path, summary_path]:
        print(path)


if __name__ == "__main__":
    main()
