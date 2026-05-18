import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from _paths import OUTPUTS_DIR, RAW_SCORES, RAW_TAXONOMY

BASE = str(OUTPUTS_DIR)
SCORES = str(RAW_SCORES)
TAXONOMY = str(RAW_TAXONOMY)


def load_long_df():
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
    return df


def fit_gee(df, formula):
    return smf.gee(
        formula,
        groups=df["Number"],
        data=df,
        family=sm.families.Binomial(),
        cov_struct=sm.cov_struct.Exchangeable(),
    ).fit()


def wald_frame(result, model_label, factor_map=None):
    wf = result.wald_test_terms().summary_frame().reset_index()
    wf = wf.rename(
        columns={
            "index": "factor",
            "chi2": "wald_chi2",
            "P>chi2": "p_value",
            "df constraint": "df",
        }
    )
    if factor_map:
        wf["factor"] = wf["factor"].map(lambda x: factor_map.get(x, x))
    wf["wald_chi2"] = (
        wf["wald_chi2"]
        .astype(str)
        .str.replace("[", "", regex=False)
        .str.replace("]", "", regex=False)
        .astype(float)
    )
    wf["model"] = model_label
    keep = ["model", "factor", "wald_chi2", "df", "p_value"]
    wf = wf[keep]
    return wf


def main():
    primary = pd.read_csv(f"{BASE}/high_journal_primary_gee_wald.csv").copy()
    primary["model"] = "Primary clustered GEE"

    simplified = pd.read_csv(f"{BASE}/clean_gee_joint_wald.csv").copy()
    simplified["model"] = "Simplified clustered GEE"
    if "factor" not in simplified.columns:
        simplified = simplified.rename(columns={"term": "factor"})

    df = load_long_df()
    expanded_formula = """Failure ~
        C(Knowledge, Treatment(reference='Factual')) +
        C(Cognitive, Treatment(reference='Remember')) +
        C(Complexity, Treatment(reference='Low')) +
        C(Risk, Treatment(reference='Low')) +
        C(Difficulty, Treatment(reference='Low')) +
        C(Task, Treatment(reference='1_Physiology_and_Pathophysiology'))"""
    expanded = fit_gee(df, expanded_formula)
    factor_map = {
        "C(Knowledge, Treatment(reference='Factual'))": "Knowledge",
        "C(Cognitive, Treatment(reference='Remember'))": "Cognitive",
        "C(Complexity, Treatment(reference='Low'))": "Complexity",
        "C(Risk, Treatment(reference='Low'))": "Risk",
        "C(Difficulty, Treatment(reference='Low'))": "Difficulty",
        "C(Task, Treatment(reference='1_Physiology_and_Pathophysiology'))": "Task",
    }
    expanded_wald = wald_frame(expanded, "Expanded exploratory GEE", factor_map)
    expanded_wald.to_csv(f"{BASE}/full_exploratory_remember_joint_wald.csv", index=False)

    keep_cols = ["model", "factor", "wald_chi2", "df", "p_value"]
    all_df = pd.concat(
        [
            primary[keep_cols],
            simplified[keep_cols],
            expanded_wald[keep_cols],
        ],
        ignore_index=True,
    )
    all_df["wald_chi2"] = (
        all_df["wald_chi2"]
        .astype(str)
        .str.replace("[", "", regex=False)
        .str.replace("]", "", regex=False)
        .astype(float)
    )
    all_df["p_value"] = all_df["p_value"].astype(float)
    all_df = all_df.sort_values(["model", "factor"]).reset_index(drop=True)
    all_df.to_csv(f"{BASE}/TableS6_Joint_Wald_Comparison.csv", index=False)

    print(all_df.to_string(index=False))
    print(f"\nSaved {BASE}/full_exploratory_remember_joint_wald.csv")
    print(f"Saved {BASE}/TableS6_Joint_Wald_Comparison.csv")


if __name__ == "__main__":
    main()
