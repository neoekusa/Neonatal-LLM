"""Question-clustered estimates for the recorded panel of web-interface evaluations."""

import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from patsy import build_design_matrices, dmatrix
from scipy.special import expit, logit
from scipy.stats import chi2, norm
from statsmodels.stats.multitest import multipletests
from statsmodels.stats.outliers_influence import variance_inflation_factor


REFERENCES = {
    "Cognitive": "Remember",
    "Complexity": "Low",
    "Task": "1_Physiology_and_Pathophysiology",
    "Knowledge": "Factual",
    "Risk": "Low",
    "Difficulty": "Low",
}
SIMPLE = ["Cognitive", "Complexity"]
PRIMARY = [*SIMPLE, "Task"]
EXPANDED = [*PRIMARY, "Knowledge", "Risk", "Difficulty"]
Z95 = norm.ppf(0.975)


def reference_code(df):
    """Make reference levels explicit, including for the model-identity sensitivity."""
    df = df.copy()
    models = sorted(df["Model"].unique())
    # Preserve the published panel's fixed-effects reference when display labels change.
    refs = {**REFERENCES, "Model": "ChatGPT-4o" if "ChatGPT-4o" in models else models[0]}
    for field, reference in refs.items():
        levels = set(df[field].unique())
        if reference not in levels:
            raise ValueError(f"Missing {field} reference level {reference!r}")
        categories = [reference, *sorted(levels - {reference})]
        df[field] = pd.Categorical(df[field], categories=categories)
    return df


def fit_gee(df, factors):
    formula = "Failure ~ " + " + ".join(factors)
    model = smf.gee(formula, groups="Number", data=df, missing="raise",
                    family=sm.families.Binomial(), cov_struct=sm.cov_struct.Exchangeable())
    if np.linalg.matrix_rank(model.exog) != model.exog.shape[1]:
        raise ValueError(f"Nonidentifiable GEE design: {formula}")
    result = model.fit(scale=1, cov_type="robust")
    if not result.converged or not np.isfinite(result.params).all():
        raise RuntimeError(f"GEE did not converge: {formula}")
    cov = result.cov_params().to_numpy()
    if not np.isfinite(cov).all() or np.linalg.eigvalsh(cov).min() < -1e-8:
        raise RuntimeError(f"Invalid robust covariance: {formula}")
    return result


def coefficient_table(result, df, factors, model_name, linear=False):
    rows = []
    intervals = result.conf_int()
    slices = result.model.data.design_info.term_name_slices
    for factor in factors:
        levels = df[factor].cat.categories
        counts = df.groupby(factor, observed=True).agg(questions=("Number", "nunique"),
                                                        responses=("Failure", "size"), failures=("Failure", "sum"))
        for term, level in zip(result.params.index[slices[factor]], levels[1:], strict=True):
            values = np.r_[result.params[term], intervals.loc[term].values]
            point, low, high = values if linear else np.exp(values)
            rows.append({
                "model": model_name, "factor": factor, "level": level, "reference": levels[0],
                "risk_difference" if linear else "odds_ratio": point,
                "ci_low": low, "ci_high": high, "p_value": result.pvalues[term],
                "coefficient": result.params[term], "standard_error": result.bse[term],
                "level_questions": counts.loc[level, "questions"], "ref_questions": counts.loc[levels[0], "questions"],
                "level_responses": counts.loc[level, "responses"], "ref_responses": counts.loc[levels[0], "responses"],
                "level_failures": counts.loc[level, "failures"], "ref_failures": counts.loc[levels[0], "failures"],
            })
    table = pd.DataFrame(rows)
    cognitive = table["factor"].eq("Cognitive")
    if cognitive.any():
        table.loc[cognitive, "cognitive_p_holm"] = multipletests(
            table.loc[cognitive, "p_value"], method="holm")[1]
    return table


def wald_table(result, factors, name):
    rows = []
    covariance = result.cov_params().to_numpy()
    for factor in factors:
        block = result.model.data.design_info.term_name_slices[factor]
        b = result.params.to_numpy()[block]
        cov = covariance[block, block]
        if np.linalg.eigvalsh(cov).min() <= np.linalg.norm(cov, 2) * 1e-10:
            raise RuntimeError(f"Unestimable joint test for {factor} in {name}")
        stat = float(b @ np.linalg.solve(cov, b))
        rows.append({"model": name, "factor": factor, "wald_chi2": stat, "df": len(b),
                     "p_value": chi2.sf(stat, len(b))})
    return pd.DataFrame(rows)


def fit_summary(result, df, name, factors):
    cov = result.cov_params().to_numpy()
    qic, qicu = result.qic(scale=1)
    return {
        "model": name, "factors": " + ".join(factors), "questions": df["Number"].nunique(),
        "models": df["Model"].nunique(), "responses": len(df),
        "design_columns": result.model.exog.shape[1],
        "design_rank": np.linalg.matrix_rank(result.model.exog),
        "covariance_rank_relative_tol_1e_10": np.linalg.matrix_rank(cov, tol=np.linalg.norm(cov, 2) * 1e-10),
        "working_correlation": float(result.cov_struct.dep_params),
        "qic": qic, "qicu": qicu, "status": "fitted",
    }


def marginal_tables(result, df):
    """Equal-weight standardization over observed items; hold their covariate mix fixed."""
    items = df.drop_duplicates("Number").copy()
    profiles = ["Cognitive", "Task"]
    item_profiles = pd.MultiIndex.from_frame(items[profiles])
    covariance = result.cov_params().to_numpy()
    rows, differences = [], []
    for level in ["Low", "Moderate", "High"]:
        assigned = items.assign(Complexity=level)
        design, = build_design_matrices([result.model.data.design_info], assigned)
        X = np.asarray(design)
        probabilities = expit(X @ result.params.to_numpy())
        prediction = probabilities.mean()
        gradient = (X * (probabilities * (1 - probabilities))[:, None]).mean(axis=0)
        logit_se = np.sqrt(gradient @ covariance @ gradient) / (prediction * (1 - prediction))
        limits = expit(logit(prediction) + np.array([-Z95, Z95]) * logit_se)
        observed = pd.MultiIndex.from_frame(items.loc[items["Complexity"] == level, profiles])
        rows.append({"complexity": level, "predicted_failure": prediction,
                     "ci_low": limits[0], "ci_high": limits[1], "questions_total": len(items),
                     "questions_outside_support": int((~item_profiles.isin(observed)).sum())})
        if level == "Low":
            base_prediction, base_gradient = prediction, gradient
        else:
            difference = prediction - base_prediction
            derivative = gradient - base_gradient
            se = np.sqrt(derivative @ covariance @ derivative)
            differences.append({"complexity": level, "reference": "Low", "risk_difference": difference,
                                "ci_low": difference - Z95 * se, "ci_high": difference + Z95 * se})
    return pd.DataFrame(rows), pd.DataFrame(differences)


def run(df, out):
    """Write full-precision estimates; callers supply validated panel data and a staging directory."""
    df = reference_code(df)
    primary = fit_gee(df, PRIMARY)
    coefficient_table(primary, df, PRIMARY, "primary").to_csv(out / "primary_coefficients.csv", index=False)
    wald_table(primary, PRIMARY, "primary").to_csv(out / "primary_wald.csv", index=False)
    marginals, differences = marginal_tables(primary, df)
    marginals.to_csv(out / "marginals.csv", index=False)
    differences.to_csv(out / "marginal_differences.csv", index=False)
    fits = [fit_summary(primary, df, "primary", PRIMARY)]

    items = df.drop_duplicates("Number")
    design = dmatrix(" + ".join(EXPANDED), items, return_type="dataframe")
    ncol = design.shape[1]
    rank = np.linalg.matrix_rank(design)
    fits.append({"model": "full_taxonomy", "factors": " + ".join(EXPANDED),
                 "questions": len(items), "models": df["Model"].nunique(), "responses": len(df),
                 "design_columns": ncol, "design_rank": rank,
                 "status": "not fitted: aliased design" if rank < ncol else "diagnostic only"})
    primary_design = dmatrix(" + ".join(PRIMARY), items, return_type="dataframe")
    vif = [{"term": col, "vif": variance_inflation_factor(primary_design.to_numpy(), i)}
           for i, col in enumerate(primary_design) if col != "Intercept"]
    pd.DataFrame(vif).to_csv(out / "primary_dummy_vif.csv", index=False)

    # Recode both sparse labels only in the exploratory sensitivity.
    collapsed = df.assign(Knowledge=df["Knowledge"].astype(str).replace("Metacognitive", "Conceptual"),
                          Cognitive=df["Cognitive"].astype(str).replace("Evaluate", "Analyze"))
    collapsed = reference_code(collapsed)
    coef, tests = [], []
    comparisons = [
        ("simplified", df, SIMPLE),
        ("llm_fixed_effects", df, [*PRIMARY, "Model"]),
        ("collapsed_exploratory", collapsed, EXPANDED),
    ]
    for name, analysis, factors in comparisons:
        result = fit_gee(analysis, factors)
        fits.append(fit_summary(result, analysis, name, factors))
        coef.append(coefficient_table(result, analysis, factors, name))
        tests.append(wald_table(result, factors, name))
    pd.concat(coef, ignore_index=True).to_csv(out / "sensitivity_coefficients.csv", index=False)
    pd.concat(tests, ignore_index=True).to_csv(out / "sensitivity_wald.csv", index=False)
    pd.DataFrame(fits).to_csv(out / "gee_model_fit.csv", index=False)

    # The outcome is failure; a positive difference denotes a higher absolute risk.
    lpm = smf.ols("Failure ~ " + " + ".join(SIMPLE), data=df, missing="raise").fit(
        cov_type="cluster", cov_kwds={"groups": df["Number"], "use_correction": True}, use_t=True)
    linear = coefficient_table(lpm, df, SIMPLE, "simplified_lpm", linear=True)
    linear["reference_df"] = lpm.df_resid_inference
    linear.to_csv(out / "linear_probability.csv", index=False)

    omissions = []
    for model in sorted(df["Model"].unique()):
        subset = df.loc[df["Model"] != model]
        fitted = fit_gee(subset, PRIMARY)
        rows = coefficient_table(fitted, subset, ["Complexity"], "leave_one_model_out")
        rows["omitted_model"] = model
        rows["models_remaining"] = subset["Model"].nunique()
        rows["responses"] = len(subset)
        omissions.append(rows)
    pd.concat(omissions, ignore_index=True).to_csv(out / "leave_one_model_out.csv", index=False)
