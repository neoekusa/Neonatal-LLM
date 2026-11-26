"""Question-level descriptions and paired comparisons for the v4 benchmark."""
from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import chi2_contingency
from statsmodels.stats.contingency_tables import cochrans_q
from statsmodels.stats.proportion import proportion_confint


PRIMARY_FACTORS = ["Complexity", "Cognitive", "Task"]
FULL_FACTORS = ["Complexity", "Cognitive", "Task", "Knowledge", "Risk", "Difficulty"]
PROVIDERS = {
    "ChatGPT": "OpenAI", "Gemini": "Google", "Gemma": "Google", "Grok": "xAI",
    "DeepSeek": "DeepSeek", "Claude": "Anthropic", "Llama": "Meta",
}


def accuracy_table(correct):
    correct_counts = correct.sum().astype(int)
    n = len(correct)
    low, high = proportion_confint(correct_counts, n, method="wilson")
    rows = pd.DataFrame({
        "model": correct.columns,
        "provider": [next((v for k, v in PROVIDERS.items() if model.startswith(k)), "Unspecified")
                     for model in correct.columns],
        "questions": n, "correct": correct_counts.to_numpy(), "incorrect": n - correct_counts.to_numpy(),
        "accuracy": correct_counts.to_numpy() / n, "ci_low": np.asarray(low), "ci_high": np.asarray(high),
    })
    return rows.sort_values(["correct", "model"], ascending=[False, True])


def paired_comparisons(correct, out):
    discordant = correct.nunique(axis=1).gt(1).sum()
    statistic, p_value = np.nan, np.nan
    if discordant:
        test = cochrans_q(correct.to_numpy())
        statistic, p_value = test.statistic, test.pvalue
    pd.DataFrame([{
        "questions": len(correct), "models": correct.shape[1], "discordant_questions": discordant,
        "q_statistic": statistic, "df": correct.shape[1] - 1, "p_value": p_value,
    }]).to_csv(out / "cochran_q.csv", index=False)
    correlation = (1 - correct).corr(method="spearman")
    correlation.to_csv(out / "error_correlations.csv", index_label="model")
    pairs = [(first, second, correlation.loc[first, second]) for first, second in combinations(correct.columns, 2)]
    pd.DataFrame(pairs, columns=["model_1", "model_2", "spearman_rho"]).sort_values(
        ["spearman_rho", "model_1", "model_2"], ascending=[False, True, True]
    ).to_csv(out / "error_pairs.csv", index=False)


def consensus_items(df):
    """At least half failed; tabulate only wrong single-option answers as distractors."""
    rows = []
    for q, group in df.groupby("Number", sort=True):
        failed = group.loc[group["Failure"].eq(1), "Answer"].str.strip()
        if len(failed) * 2 < len(group):
            continue
        item = group.iloc[0]
        counts = failed.value_counts()
        options = counts.reindex(list("ABCDE"), fill_value=0)
        modal_count = int(options.max())
        modal_options = options.index[options.eq(modal_count)].tolist() if modal_count else []
        invalid = counts[~counts.index.isin(options.index)].sort_index()
        rows.append({
            "question": q, "models": len(group), "models_failed": len(failed), "answer_key": item["RealAnswer"],
            "domain": item["Main Domain"], "subdomain": item["Subdomain"],
            "complexity": item["Complexity"], "risk": item["Risk"],
            "modal_wrong_options": "|".join(modal_options), "models_per_modal_option": modal_count,
            **{f"wrong_{label}": int(n) for label, n in options.items()},
            "non_single_responses": int(invalid.sum()),
            "non_single_breakdown": " | ".join(f"{label} ({n})" for label, n in invalid.items()),
        })
    columns = ["question", "models", "models_failed", "answer_key", "domain", "subdomain", "complexity",
               "risk", "modal_wrong_options", "models_per_modal_option", *(f"wrong_{x}" for x in "ABCDE"),
               "non_single_responses", "non_single_breakdown"]
    return pd.DataFrame(rows, columns=columns).sort_values(["models_failed", "question"], ascending=[False, True])


def stratum_counts(items, factors):
    """One row per potential combination. Empty cells have no defined failure rate."""
    counts = items.groupby(factors, observed=True).agg(
        questions=("Number", "size"), incorrect=("incorrect", "sum"), responses=("responses", "sum")
    )
    levels = [sorted(items[f].unique()) for f in factors]
    index = pd.MultiIndex.from_product(levels, names=factors)
    counts = counts.reindex(index, fill_value=0)
    counts["observed_failure"] = counts.incorrect / counts.responses.where(counts.responses.gt(0))
    return counts.reset_index()


def describe_taxonomy(items, out):
    category_rows = []
    for factor in [*FULL_FACTORS, "Main Domain", "Main Guideline", "Subdomain"]:
        counts = items.groupby(factor, observed=True).agg(
            questions=("Number", "size"), incorrect=("incorrect", "sum"), responses=("responses", "sum")
        ).rename_axis("level").reset_index()
        counts.insert(0, "factor", factor)
        counts["observed_failure"] = counts.incorrect / counts.responses
        category_rows.append(counts)
    pd.concat(category_rows).to_csv(out / "observed_by_category.csv", index=False)

    support_rows = []
    for name, factors in [("complexity_by_cognitive", PRIMARY_FACTORS[:2]),
                          ("primary_strata", PRIMARY_FACTORS), ("full_strata", FULL_FACTORS)]:
        counts = stratum_counts(items, factors)
        counts.to_csv(out / f"{name}.csv", index=False)
        n = counts.questions
        support_rows.append({
            "table": name, "possible_cells": len(n), "occupied": n.gt(0).sum(),
            "empty": n.eq(0).sum(), "singleton": n.eq(1).sum(), "occupied_with_1_to_4_questions": n.between(1, 4).sum(),
            "questions": n.sum(),
        })
    pd.DataFrame(support_rows).to_csv(out / "strata_summary.csv", index=False)

    cramers_v = pd.DataFrame(np.eye(len(FULL_FACTORS)), index=FULL_FACTORS, columns=FULL_FACTORS)
    for first, second in combinations(FULL_FACTORS, 2):
        cells = pd.crosstab(items[first], items[second])
        dim = min(cells.shape) - 1
        v = np.sqrt(chi2_contingency(cells, correction=False).statistic / (len(items) * dim)) if dim else np.nan
        cramers_v.loc[first, second] = cramers_v.loc[second, first] = v
    cramers_v.to_csv(out / "cramers_v.csv", index_label="factor")


def run(df, out: Path):
    """Use the validated, complete question-by-model panel supplied by the runner."""
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    correct = df.pivot(index="Number", columns="Model", values="Correct").sort_index()
    if correct.isna().any().any():
        raise ValueError("Paired comparisons require a complete question-by-model panel.")
    accuracy = accuracy_table(correct)
    accuracy.to_csv(out / "accuracy.csv", index=False)
    correct[accuracy.model].to_csv(out / "question_correctness.csv", index_label="question")
    non_single = df.loc[~df["Answer"].str.strip().isin(list("ABCDE")), ["Number", "Model", "Answer", "RealAnswer"]]
    non_single.rename(columns={"Number": "question", "Model": "model", "Answer": "response",
                               "RealAnswer": "answer_key"}).sort_values(["question", "model"]).to_csv(
        out / "non_single_responses.csv", index=False
    )
    paired_comparisons(correct, out)
    consensus_items(df).to_csv(out / "consensus_items.csv", index=False)
    items = df.drop_duplicates("Number").set_index("Number")
    items["incorrect"] = (1 - correct).sum(axis=1)
    items["responses"] = correct.shape[1]
    describe_taxonomy(items.reset_index(), out)
