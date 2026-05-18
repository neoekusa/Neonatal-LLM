import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import chi2_contingency
from matplotlib.colors import LinearSegmentedColormap
from sklearn.preprocessing import LabelEncoder
from statsmodels.stats.outliers_influence import variance_inflation_factor
from _paths import OUTPUTS_DIR, RAW_TAXONOMY

TAX_PATH = str(RAW_TAXONOMY)
OUT_DIR = str(OUTPUTS_DIR)


def cramers_v(x, y):
    tab = pd.crosstab(x, y)
    chi2 = chi2_contingency(tab, correction=False)[0]
    n = tab.to_numpy().sum()
    r, k = tab.shape
    phi2 = chi2 / n
    phi2corr = max(0, phi2 - ((k - 1) * (r - 1)) / (n - 1))
    rcorr = r - ((r - 1) ** 2) / (n - 1)
    kcorr = k - ((k - 1) ** 2) / (n - 1)
    denom = min(kcorr - 1, rcorr - 1)
    if denom <= 0:
        return np.nan
    return np.sqrt(phi2corr / denom)


def load_taxonomy():
    q = pd.read_csv(TAX_PATH)
    q.columns = [c.strip() for c in q.columns]
    q = q.rename(
        columns={
            "Knowledge Dimension": "Knowledge Dimension",
            "Cognitive Process": "Cognitive Process",
            "Reasoning  Complexity": "Reasoning Complexity",
            "Clinical Risk": "Clinical Risk",
            "Universal Task Category": "Universal Task",
        }
    )
    cols = [
        "Reasoning Complexity",
        "Knowledge Dimension",
        "Cognitive Process",
        "Clinical Risk",
        "Universal Task",
    ]
    return q[cols].copy()


def make_cramers_v(q):
    cols = list(q.columns)
    cv = pd.DataFrame(index=cols, columns=cols, dtype=float)
    for a in cols:
        for b in cols:
            cv.loc[a, b] = 1.0 if a == b else cramers_v(q[a], q[b])
    cv.to_csv(f"{OUT_DIR}/verified_cramers_v_matrix.csv")

    cmap = LinearSegmentedColormap.from_list(
        "cramers_pub",
        ["#2b1d4f", "#4257a4", "#3f8fb3", "#59c3b3", "#dff2e1"],
        N=256,
    )

    plt.figure(figsize=(8.8, 7.2))
    ax = sns.heatmap(
        cv,
        annot=False,
        cmap=cmap,
        vmin=0,
        vmax=1,
        square=True,
        linewidths=0.5,
        linecolor="white",
        cbar_kws={"label": "Cramer's V Value"},
    )

    for i in range(cv.shape[0]):
        for j in range(cv.shape[1]):
            val = cv.iloc[i, j]
            txt_color = "black" if val >= 0.72 else "white"
            ax.text(
                j + 0.5,
                i + 0.5,
                f"{val:.2f}",
                ha="center",
                va="center",
                fontsize=11,
                fontweight="bold",
                color=txt_color,
            )

    plt.xticks(rotation=45, ha="right", fontsize=10, fontweight="bold")
    plt.yticks(rotation=0, fontsize=10, fontweight="bold")
    plt.tight_layout()
    path = f"{OUT_DIR}/verified_cramers_v_matrix.png"
    plt.savefig(path, dpi=300, bbox_inches="tight")
    plt.close()
    return path


def make_vif(q):
    enc = pd.DataFrame()
    for c in q.columns:
        le = LabelEncoder()
        enc[c] = le.fit_transform(q[c].astype(str))

    vif_df = pd.DataFrame(
        {
            "Variable": list(enc.columns),
            "VIF": [variance_inflation_factor(enc.values, i) for i in range(enc.shape[1])],
        }
    ).sort_values("VIF", ascending=False)
    vif_df.to_csv(f"{OUT_DIR}/verified_vif_values.csv", index=False)

    colors = ["#b00020" if v > 5 else "#6baed6" for v in vif_df["VIF"]]
    plt.figure(figsize=(9.4, 5.8))
    ax = sns.barplot(data=vif_df, x="VIF", y="Variable", hue="Variable", palette=colors, legend=False)
    max_vif = float(vif_df["VIF"].max())
    x_max = max(5.8, max_vif + 0.9)
    ax.set_xlim(0, x_max)
    ax.axvline(x=5, color="#b00020", linestyle="--", linewidth=1.2)
    ax.text(
        5.03,
        -0.42,
        "VIF = 5",
        color="#b00020",
        fontsize=10,
        fontweight="bold",
        ha="left",
        va="bottom",
    )
    plt.xlabel("Variance inflation factor")
    plt.ylabel("")
    plt.tight_layout()
    path = f"{OUT_DIR}/verified_vif_values.png"
    plt.savefig(path, dpi=300, bbox_inches="tight")
    plt.close()
    return path


def main():
    q = load_taxonomy()
    p1 = make_cramers_v(q)
    p2 = make_vif(q)
    print(p1)
    print(p2)


if __name__ == "__main__":
    main()
