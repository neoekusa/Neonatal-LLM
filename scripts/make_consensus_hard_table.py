import math

import pandas as pd

from _paths import OUTPUTS_DIR, RAW_SCORES, RAW_TAXONOMY


def load_data():
    scores = pd.read_csv(RAW_SCORES)
    tax = pd.read_csv(RAW_TAXONOMY)
    scores.columns = [c.strip() for c in scores.columns]
    tax.columns = [c.strip() for c in tax.columns]
    return scores, tax


def build_consensus_hard_table(scores: pd.DataFrame, tax: pd.DataFrame) -> pd.DataFrame:
    model_cols = [c for c in scores.columns if c not in ["Number", "RealAnswer"]]
    n_models = len(model_cols)
    threshold = math.ceil(n_models / 2)

    error_counts = (
        scores[model_cols]
        .astype(str)
        .apply(lambda col: col.str.strip())
        .ne(scores["RealAnswer"].astype(str).str.strip(), axis=0)
        .sum(axis=1)
    )

    out = pd.DataFrame(
        {
            "Number": scores["Number"].astype(int),
            "Models Failed": error_counts.astype(int),
        }
    )

    tax_subset = tax.rename(
        columns={
            "Q No": "Number",
            "Main Domain": "Main_Domain",
            "Reasoning  Complexity": "Complexity",
            "Clinical Risk": "Risk",
        }
    )[["Number", "Main_Domain", "Subdomain", "Complexity", "Risk"]]

    out = out.merge(tax_subset, on="Number", how="left")
    out = out.loc[out["Models Failed"] >= threshold].copy()
    out = out.sort_values(["Models Failed", "Number"], ascending=[False, True]).reset_index(drop=True)
    return out


def main():
    scores, tax = load_data()
    out = build_consensus_hard_table(scores, tax)
    out.to_csv(f"{OUTPUTS_DIR}/TableS2_Consensus_Hard_Questions.csv", index=False)
    print(f"Saved {OUTPUTS_DIR}/TableS2_Consensus_Hard_Questions.csv")
    print(out.to_string(index=False))


if __name__ == "__main__":
    main()
