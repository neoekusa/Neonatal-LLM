import itertools
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from scipy.stats import spearmanr
from statsmodels.stats.contingency_tables import cochrans_q

from _model_labels import standardize_model_label
from _paths import OUTPUTS_DIR, RAW_SCORES, RAW_TAXONOMY

BASE = Path(OUTPUTS_DIR)
SCORES = Path(RAW_SCORES)
TAXONOMY = Path(RAW_TAXONOMY)


def _clean_cat(series: pd.Series) -> pd.Series:
    return (
        series.astype(str)
        .str.strip()
        .str.replace(" ", "_", regex=False)
        .str.replace(".", "", regex=False)
        .str.replace("/", "_", regex=False)
    )


def load_data():
    scores_df = pd.read_csv(SCORES)
    tax_df = pd.read_csv(TAXONOMY)
    scores_df.columns = [c.strip() for c in scores_df.columns]
    tax_df.columns = [c.strip() for c in tax_df.columns]

    model_cols = [c for c in scores_df.columns if c not in ["Number", "RealAnswer"]]
    display_model_cols = [standardize_model_label(c) for c in model_cols]
    rename_map = dict(zip(model_cols, display_model_cols))

    long_df = scores_df.melt(
        id_vars=["Number", "RealAnswer"],
        value_vars=model_cols,
        var_name="Model",
        value_name="Answer",
    )
    long_df["Model"] = long_df["Model"].map(rename_map)
    long_df["Correct"] = (
        long_df["Answer"].astype(str).str.strip()
        == long_df["RealAnswer"].astype(str).str.strip()
    ).astype(int)
    long_df["Failure"] = 1 - long_df["Correct"]

    tax_clean = tax_df.rename(
        columns={
            "Q No": "Q_No",
            "Knowledge Dimension": "Knowledge_Dimension",
            "Cognitive Process": "Cognitive_Process",
            "Reasoning  Complexity": "Reasoning_Complexity",
            "Clinical Risk": "Clinical_Risk",
            "Difficulty": "Difficulty",
            "Universal Task Category": "Universal_Task_Category",
        }
    )

    merged = pd.merge(long_df, tax_clean, left_on="Number", right_on="Q_No")
    for col in [
        "Knowledge_Dimension",
        "Cognitive_Process",
        "Reasoning_Complexity",
        "Clinical_Risk",
        "Difficulty",
        "Universal_Task_Category",
    ]:
        merged[col] = _clean_cat(merged[col])

    wide_correct = pd.DataFrame({"Number": scores_df["Number"]})
    wide_error = pd.DataFrame({"Number": scores_df["Number"]})
    for raw, disp in rename_map.items():
        correct = (
            scores_df[raw].astype(str).str.strip()
            == scores_df["RealAnswer"].astype(str).str.strip()
        ).astype(int)
        wide_correct[disp] = correct
        wide_error[disp] = 1 - correct

    return scores_df, tax_df, merged, wide_correct, wide_error, display_model_cols


def write_accuracy_outputs(wide_correct: pd.DataFrame, model_cols):
    counts = []
    n_questions = len(wide_correct)
    for model in model_cols:
        correct = int(wide_correct[model].sum())
        wrong = n_questions - correct
        acc = 100 * correct / n_questions
        counts.append(
            {
                "Model": model,
                "Correct": correct,
                "Wrong": wrong,
                "Accuracy (%)": round(acc, 2),
            }
        )
    acc_df = pd.DataFrame(counts).sort_values(
        ["Correct", "Model"], ascending=[False, True]
    ).reset_index(drop=True)
    acc_df.index = acc_df.index + 1
    acc_df.to_csv(BASE / "Table1_Model_Accuracy.csv")
    acc_df.to_csv(BASE / "model_accuracy_report.csv", index=False)

    gee_error = acc_df.copy()
    gee_error["Error_Rate"] = gee_error["Wrong"] / n_questions
    gee_error["Error_Rate_Percent"] = 100 * gee_error["Error_Rate"]
    gee_error[["Model", "Error_Rate", "Correct", "Error_Rate_Percent"]].rename(
        columns={"Correct": "n_questions"}
    ).to_csv(BASE / "gee_model_error_rates.csv", index=False)


def fit_primary_model(df):
    formula = (
        "Failure ~ "
        "C(Cognitive_Process, Treatment(reference='Remember')) + "
        "C(Reasoning_Complexity, Treatment(reference='Low')) + "
        "C(Universal_Task_Category, Treatment(reference='1_Physiology_and_Pathophysiology'))"
    )
    return smf.gee(
        formula,
        groups=df["Number"],
        data=df,
        family=sm.families.Binomial(),
        cov_struct=sm.cov_struct.Exchangeable(),
    ).fit(scale=1.0)


def write_primary_model_outputs(result):
    coef = pd.DataFrame(
        {
            "term": result.params.index,
            "coef_log_odds": result.params.values,
            "se": result.bse.values,
            "p_value": result.pvalues.values,
        }
    )
    coef["odds_ratio"] = np.exp(coef["coef_log_odds"])
    coef["ci_low"] = np.exp(coef["coef_log_odds"] - 1.96 * coef["se"])
    coef["ci_high"] = np.exp(coef["coef_log_odds"] + 1.96 * coef["se"])
    coef["is_intercept"] = coef["term"].eq("Intercept")
    coef.to_csv(BASE / "high_journal_primary_gee_coefficients.csv", index=False)

    wt = result.wald_test_terms(skip_single=False).table.reset_index()
    wt = wt.rename(columns={"index": "factor"})
    rows = []
    factor_map = {
        "C(Cognitive_Process, Treatment(reference='Remember'))": "Cognitive_Process",
        "C(Reasoning_Complexity, Treatment(reference='Low'))": "Reasoning_Complexity",
        "C(Universal_Task_Category, Treatment(reference='1_Physiology_and_Pathophysiology'))": "Universal_Task_Category",
    }
    for raw_name, display_name in factor_map.items():
        row = wt.loc[wt["factor"] == raw_name].iloc[0]
        rows.append(
            {
                "factor": display_name,
                "wald_chi2": float(np.asarray(row["statistic"]).reshape(-1)[0]),
                "df": int(row["df_constraint"]),
                "p_value": float(row["pvalue"]),
            }
        )
    wald_df = pd.DataFrame(rows)
    wald_df.to_csv(BASE / "high_journal_primary_gee_wald.csv", index=False)

    qic, qicu = result.qic(scale=1.0)
    pd.DataFrame([{"qic": float(qic), "qicu": float(qicu)}]).to_csv(
        BASE / "high_journal_primary_qic_qicu.csv", index=False
    )

    summary_rows = [
        {"section": "Primary model", "detail": "Question-clustered GEE with exchangeable correlation"},
        {
            "section": "References",
            "detail": "Cognitive process=Remember; Reasoning complexity=Low; Task category=Physiology/Pathophysiology",
        },
        {"section": "Model fit", "detail": f"QIC={float(qic):.2f}; QICu={float(qicu):.2f}"},
    ]
    for _, row in wald_df.iterrows():
        summary_rows.append(
            {
                "section": f"Wald: {row['factor']}",
                "detail": f"chi-square={row['wald_chi2']:.2f}, df={int(row['df'])}, p={row['p_value']:.3f}",
            }
        )
    pd.DataFrame(summary_rows).to_csv(BASE / "high_journal_primary_summary.csv", index=False)

    table2_rows = [
        {"Factor": "Cognitive Process", "Category": "Remember (Ref)", "aOR": 1.0, "p-value": "-", "95% CI": "-"},
        {"Factor": "Reasoning Complexity", "Category": "Low (Ref)", "aOR": 1.0, "p-value": "-", "95% CI": "-"},
        {"Factor": "Universal Task Category", "Category": "1 Physiology and Pathophysiology (Ref)", "aOR": 1.0, "p-value": "-", "95% CI": "-"},
    ]
    label_map = {
        "C(Cognitive_Process, Treatment(reference='Remember'))[T.Analyze]": ("Cognitive Process", "Analyze"),
        "C(Cognitive_Process, Treatment(reference='Remember'))[T.Apply]": ("Cognitive Process", "Apply"),
        "C(Cognitive_Process, Treatment(reference='Remember'))[T.Evaluate]": ("Cognitive Process", "Evaluate"),
        "C(Cognitive_Process, Treatment(reference='Remember'))[T.Understand]": ("Cognitive Process", "Understand"),
        "C(Reasoning_Complexity, Treatment(reference='Low'))[T.High]": ("Reasoning Complexity", "High"),
        "C(Reasoning_Complexity, Treatment(reference='Low'))[T.Moderate]": ("Reasoning Complexity", "Moderate"),
        "C(Universal_Task_Category, Treatment(reference='1_Physiology_and_Pathophysiology'))[T.2_Epidemiology_and_Risk_Assessment]": ("Universal Task Category", "2 Epidemiology and Risk Assessment"),
        "C(Universal_Task_Category, Treatment(reference='1_Physiology_and_Pathophysiology'))[T.3_Diagnosis]": ("Universal Task Category", "3 Diagnosis"),
        "C(Universal_Task_Category, Treatment(reference='1_Physiology_and_Pathophysiology'))[T.4_Management_and_Treatment]": ("Universal Task Category", "4 Management and Treatment"),
    }
    non_intercept = coef.loc[~coef["is_intercept"]].copy()
    for _, row in non_intercept.iterrows():
        factor, category = label_map[row["term"]]
        table2_rows.append(
            {
                "Factor": factor,
                "Category": category,
                "aOR": float(row["odds_ratio"]),
                "p-value": float(row["p_value"]),
                "95% CI": f"[{row['ci_low']:.2f}, {row['ci_high']:.2f}]",
            }
        )
    pd.DataFrame(table2_rows).to_csv(BASE / "Table2_Primary_GEE_Reduced_Model.csv", index=False)

    table3 = pd.DataFrame(
        [
            {"Predictor": "Cognitive Process", "Wald chi-square": rows[0]["wald_chi2"], "df": float(rows[0]["df"]), "p-value": rows[0]["p_value"]},
            {"Predictor": "Reasoning Complexity", "Wald chi-square": rows[1]["wald_chi2"], "df": float(rows[1]["df"]), "p-value": rows[1]["p_value"]},
            {"Predictor": "Universal Task Category", "Wald chi-square": rows[2]["wald_chi2"], "df": float(rows[2]["df"]), "p-value": rows[2]["p_value"]},
            {"Predictor": "Model fit", "Wald chi-square": "", "df": "", "p-value": ""},
            {"Predictor": "QIC", "Wald chi-square": float(qic), "df": "", "p-value": ""},
            {"Predictor": "QICu", "Wald chi-square": float(qicu), "df": "", "p-value": ""},
        ]
    )
    table3.to_csv(BASE / "Table3_Primary_Wald_and_Fit.csv", index=False)


def write_cochran_spearman_outputs(wide_error: pd.DataFrame, model_cols):
    err = wide_error[model_cols].copy()
    cq = cochrans_q(err.to_numpy())
    pd.DataFrame(
        [
            {
                "n_questions": int(err.shape[0]),
                "n_models": int(err.shape[1]),
                "cochrans_q_statistic": float(cq.statistic),
                "df": int(err.shape[1] - 1),
                "p_value": float(cq.pvalue),
            }
        ]
    ).to_csv(BASE / "TableS11_Cochrans_Q_All_Models.csv", index=False)

    corr = err.corr(method="spearman")
    corr.to_csv(BASE / "TableS12_Spearman_Error_Correlation.csv")

    pair_rows = []
    for m1, m2 in itertools.combinations(model_cols, 2):
        rho, p = spearmanr(err[m1], err[m2])
        pair_rows.append({"model_1": m1, "model_2": m2, "rho": float(rho), "p_value": float(p)})
    pair_df = pd.DataFrame(pair_rows).sort_values("rho", ascending=False).reset_index(drop=True)
    pair_df.head(20)[["model_1", "model_2", "rho"]].to_csv(
        BASE / "TableS13_Top_Spearman_Error_Pairs.csv", index=False
    )

    rho_vals = pair_df["rho"]
    summary = pd.DataFrame(
        [
            {
                "mean_pairwise_rho": float(rho_vals.mean()),
                "median_pairwise_rho": float(rho_vals.median()),
                "min_pairwise_rho": float(rho_vals.min()),
                "max_pairwise_rho": float(rho_vals.max()),
                "n_pairs": int(len(rho_vals)),
            }
        ]
    )
    summary.to_csv(BASE / "TableS14_Spearman_Error_Correlation_Summary.csv", index=False)

    lines = [
        f"Cochran's Q statistic: {float(cq.statistic):.4f}",
        f"df: {int(err.shape[1] - 1)}",
        f"p-value: {float(cq.pvalue):.5e}",
        f"Mean pairwise Spearman rho: {float(rho_vals.mean()):.4f}",
        f"Median pairwise Spearman rho: {float(rho_vals.median()):.4f}",
        f"Range pairwise Spearman rho: {float(rho_vals.min()):.4f} to {float(rho_vals.max()):.4f}",
        "Top 10 model pairs by error-pattern rho:",
    ]
    for _, row in pair_df.head(10).iterrows():
        lines.append(f"{row['model_1']} vs {row['model_2']}: rho={row['rho']:.4f}")
    (BASE / "cochrans_q_spearman_summary.txt").write_text("\n".join(lines) + "\n")


def main():
    _, _, merged, wide_correct, wide_error, model_cols = load_data()
    write_accuracy_outputs(wide_correct, model_cols)
    primary = fit_primary_model(merged)
    write_primary_model_outputs(primary)
    write_cochran_spearman_outputs(wide_error, model_cols)
    print("Saved primary accuracy, GEE, Cochran's Q, and Spearman outputs.")


if __name__ == "__main__":
    main()
