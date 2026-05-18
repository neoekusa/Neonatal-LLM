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
    result = smf.gee(
        formula,
        groups=df["Number"],
        data=df,
        family=sm.families.Binomial(),
        cov_struct=sm.cov_struct.Exchangeable(),
    ).fit()
    ql, qic, qicu = result.model.qic(result.params, scale=1.0, cov_params=result.cov_params())
    return result, float(ql), float(qic), float(qicu)


def main():
    df = load_long_df()

    candidate_formulas = {
        "minus_knowledge_difficulty_clinicalrisk": """Failure ~
            C(Cognitive, Treatment(reference='Remember')) +
            C(Complexity, Treatment(reference='Low')) +
            C(Task, Treatment(reference='1_Physiology_and_Pathophysiology'))""",
        "minus_knowledge_difficulty": """Failure ~
            C(Cognitive, Treatment(reference='Remember')) +
            C(Complexity, Treatment(reference='Low')) +
            C(Risk, Treatment(reference='Low')) +
            C(Task, Treatment(reference='1_Physiology_and_Pathophysiology'))""",
        "minus_knowledge": """Failure ~
            C(Cognitive, Treatment(reference='Remember')) +
            C(Complexity, Treatment(reference='Low')) +
            C(Risk, Treatment(reference='Low')) +
            C(Difficulty, Treatment(reference='Low')) +
            C(Task, Treatment(reference='1_Physiology_and_Pathophysiology'))""",
    }

    full_formula_remember = """Failure ~
        C(Knowledge, Treatment(reference='Factual')) +
        C(Cognitive, Treatment(reference='Remember')) +
        C(Complexity, Treatment(reference='Low')) +
        C(Risk, Treatment(reference='Low')) +
        C(Difficulty, Treatment(reference='Low')) +
        C(Task, Treatment(reference='1_Physiology_and_Pathophysiology'))"""

    full_formula_apply = """Failure ~
        C(Knowledge, Treatment(reference='Factual')) +
        C(Cognitive, Treatment(reference='Apply')) +
        C(Complexity, Treatment(reference='Low')) +
        C(Risk, Treatment(reference='Low')) +
        C(Difficulty, Treatment(reference='Low')) +
        C(Task, Treatment(reference='1_Physiology_and_Pathophysiology'))"""

    _, ql_full_remember, qic_full_remember, qicu_full_remember = fit_gee(df, full_formula_remember)
    _, ql_full_apply, qic_full_apply, qicu_full_apply = fit_gee(df, full_formula_apply)

    existing = []

    for spec, formula in candidate_formulas.items():
        _, _, qic, qicu = fit_gee(df, formula)
        existing.append(
            {
                "model_spec": spec,
                "family": "candidate_reduced_models",
                "qic": qic,
                "qicu": qicu,
            }
        )

    existing.append(
        {
            "model_spec": "primary_reduced_cognitive_complexity_task",
            "family": "primary_model",
            "qic": existing[0]["qic"],
            "qicu": existing[0]["qicu"],
        }
    )

    clean_formula = """Failure ~
        C(Cognitive, Treatment(reference='Remember')) +
        C(Complexity, Treatment(reference='Low'))"""
    _, _, clean_qic, clean_qicu = fit_gee(df, clean_formula)
    existing.append(
        {
            "model_spec": "reduced_cognitive_complexity_only",
            "family": "new_simplified_model",
            "qic": clean_qic,
            "qicu": clean_qicu,
        }
    )

    existing.append(
        {
            "model_spec": "full_taxonomy_remember_reference",
            "family": "expanded_full_model",
            "qic": qic_full_remember,
            "qicu": qicu_full_remember,
        }
    )

    out = pd.DataFrame(existing)
    out["delta_qic_vs_best"] = out["qic"] - out["qic"].min()
    out["delta_qicu_vs_best"] = out["qicu"] - out["qicu"].min()
    out = out.sort_values(["qic", "qicu"]).reset_index(drop=True)
    out.to_csv(f"{BASE}/all_model_qic_qicu_comparison.csv", index=False)

    remember_vs_apply = pd.DataFrame(
        [
            {
                "spec": "full_taxonomy_apply_reference",
                "qic": qic_full_apply,
                "qicu": qicu_full_apply,
                "not_qic_quasi_likelihood": ql_full_apply,
                "note": "Reference recoding diagnostic only; not used as separate model in QIC ranking.",
            },
            {
                "spec": "full_taxonomy_remember_reference",
                "qic": qic_full_remember,
                "qicu": qicu_full_remember,
                "not_qic_quasi_likelihood": ql_full_remember,
                "note": "Final expanded-model parameterization used in ranking.",
            },
        ]
    )
    remember_vs_apply["delta_qic"] = remember_vs_apply["qic"] - remember_vs_apply["qic"].iloc[0]
    remember_vs_apply["delta_qicu"] = remember_vs_apply["qicu"] - remember_vs_apply["qicu"].iloc[0]
    remember_vs_apply["delta_not_qic_quasi_likelihood"] = (
        remember_vs_apply["not_qic_quasi_likelihood"]
        - remember_vs_apply["not_qic_quasi_likelihood"].iloc[0]
    )
    remember_vs_apply["interpretation"] = (
        "QIC values are positive in this table. The negative column is quasi-likelihood, "
        "not QIC. Quasi-likelihood and QICu are useful for reference-coding diagnostics. "
        "The QIC trace penalty can change under recoding for this unstable expanded model, "
        "so the recoded fit is excluded from model-ranking tables."
    )
    remember_vs_apply.to_csv(f"{BASE}/full_model_reference_qic_check.csv", index=False)

    with open(f"{BASE}/all_model_qic_qicu_comparison_summary.txt", "w", encoding="utf-8") as fh:
        fh.write(out.to_string(index=False))
        fh.write("\n\nReference check:\n")
        fh.write(remember_vs_apply.to_string(index=False))

    print(out.to_string(index=False))
    print("\nReference check:")
    print(remember_vs_apply.to_string(index=False))
    print("\nSaved:")
    print(f"{BASE}/all_model_qic_qicu_comparison.csv")
    print(f"{BASE}/full_model_reference_qic_check.csv")
    print(f"{BASE}/all_model_qic_qicu_comparison_summary.txt")


if __name__ == "__main__":
    main()
