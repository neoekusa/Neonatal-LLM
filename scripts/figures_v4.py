"""Draw the four manuscript figures from the v4 result tables."""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import ticker
from matplotlib.colors import BoundaryNorm, ListedColormap
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
import numpy as np
import pandas as pd


BLUE = "#235783"
DARK = "#23343C"
GRID = "#DBE0E3"
PROVIDER_COLORS = {
    "OpenAI": "#176B65", "Google": "#3974A3", "Anthropic": "#A44C26",
    "Meta": "#73558C", "DeepSeek": "#555C63", "xAI": "#967329", "Unspecified": "#67757F",
}


def save(fig, path):
    fig.savefig(path, dpi=260, facecolor="white", bbox_inches="tight", pad_inches=0.09)
    plt.close(fig)


def accuracy_plot(out):
    data = pd.read_csv(out / "accuracy.csv")
    fig, ax = plt.subplots(figsize=(7.1, max(4, 0.23 * len(data) + 0.8)), layout="constrained")
    for i, row in enumerate(data.itertuples()):
        color = PROVIDER_COLORS.get(row.provider, PROVIDER_COLORS["Unspecified"])
        ax.hlines(i, row.ci_low * 100, row.ci_high * 100, color=color, lw=1.4)
        ax.plot(row.accuracy * 100, i, "o", color=color, ms=5)
    ax.set_yticks(np.arange(len(data)), labels=data.model)
    ax.invert_yaxis()
    ax.set_xlabel("Correct responses (%) with 95% Wilson interval")
    ax.set_xlim(max(0, np.floor(data.ci_low.min() * 10) * 10), 100)
    ax.grid(axis="x", color=GRID, lw=0.7)
    handles = [Line2D([], [], marker="o", linestyle="none", markersize=5, color=PROVIDER_COLORS[p],
                      label=p) for p in sorted(data.provider.unique())]
    ax.legend(handles=handles, loc="lower center", bbox_to_anchor=(0.5, 1.0), ncol=3,
              title="Model provider", frameon=False, columnspacing=1.6)
    save(fig, out / "figure1_accuracy.png")


def display_level(level):
    return str(level).replace("_", " ").removeprefix("1 ").removeprefix("2 ").removeprefix("3 ").removeprefix("4 ")


def primary_plot(out):
    data = pd.read_csv(out / "primary_coefficients.csv")
    fig, ax = plt.subplots(figsize=(7.1, 4.9), layout="constrained")
    labels, positions = [], []
    y = 0
    for factor, title in [("Complexity", "Reasoning complexity"), ("Cognitive", "Cognitive process"),
                          ("Task", "Task category")]:
        group = data.loc[data.factor == factor].copy()
        if group.empty:
            continue
        if factor == "Complexity":
            group = group.sort_values("level", key=lambda x: x.map({"Moderate": 0, "High": 1}))
        labels.append(f"{title} (ref. {display_level(group.reference.iloc[0])})")
        positions.append(y)
        y += 1
        for row in group.itertuples():
            labels.append("    " + display_level(row.level))
            positions.append(y)
            ax.hlines(y, row.ci_low, row.ci_high, color=BLUE, lw=1.4)
            ax.plot(row.odds_ratio, y, "o", ms=5, color=BLUE)
            y += 1
        y += 0.45
    ax.set_yticks(positions, labels=labels)
    for tick in ax.get_yticklabels():
        if "(ref." in tick.get_text():
            tick.set_weight("bold")
            tick.set_fontsize(8)
    ax.invert_yaxis()
    ax.axvline(1, color="#49555E", linestyle="--", lw=0.9)
    ax.set_xscale("log")
    ax.set_xlabel("Adjusted odds ratio for failure (95% CI, log scale)")
    ax.xaxis.set_major_locator(ticker.LogLocator(base=10, subs=(1, 2, 5), numticks=14))
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f"{x:g}"))
    ax.grid(axis="x", color=GRID, lw=0.7)
    save(fig, out / "figure2_primary.png")


def marginals_plot(out):
    categories = ["Low", "Moderate", "High"]
    marginal = pd.read_csv(out / "marginals.csv").set_index("complexity").loc[categories]
    counts = pd.read_csv(out / "observed_by_category.csv")
    observed = counts.loc[counts.factor.eq("Complexity")].set_index("level").loc[categories]
    fig, ax = plt.subplots(figsize=(6.7, 4), layout="constrained")
    x = np.arange(len(categories))
    ax.plot(x - 0.10, observed.observed_failure * 100, marker="s", linestyle="none", ms=6,
            color="#946738", label="Observed")
    ax.vlines(x + 0.10, marginal.ci_low * 100, marginal.ci_high * 100, lw=1.8, color=BLUE)
    ax.plot(x + 0.10, marginal.predicted_failure * 100, "o", ms=6, color=BLUE, label="Adjusted (95% CI)")
    ax.set_xticks(x, labels=[f"{level}\n{n} questions" for level, n in zip(categories, observed.questions)])
    ax.set_xlim(-0.45, len(categories) - 0.55)
    ax.set_ylim(0, min(100, np.ceil(max(marginal.ci_high.max(), observed.observed_failure.max()) * 20) * 5 + 2))
    ax.set_xlabel("Reasoning complexity")
    ax.set_ylabel("Failure probability (%)")
    ax.grid(axis="y", color=GRID, lw=0.7)
    ax.legend(frameon=False, loc="lower center", bbox_to_anchor=(0.5, 1.0), ncol=2)
    save(fig, out / "figure3_marginals.png")


def errors_plot(out):
    correctness = pd.read_csv(out / "question_correctness.csv", index_col="question")
    errors = 1 - correctness.loc[correctness.min(axis=1).eq(0)]
    # Break the question axis into two panels so every item and model can be identified in print.
    n_panels = 2 if len(errors) > 40 else 1
    fig, axes = plt.subplots(n_panels, 1, figsize=(7.2, n_panels * (0.14 * len(errors.columns) + 0.7)),
                             squeeze=False, layout="constrained")
    colors = ["white", BLUE]
    cmap = ListedColormap(colors)
    for ax, rows in zip(axes.flat, np.array_split(np.arange(len(errors)), n_panels)):
        if not len(rows):
            ax.axis("off")
            ax.text(0.5, 0.5, "All recorded responses were correct.", ha="center", transform=ax.transAxes)
            continue
        block = errors.iloc[rows]
        ax.imshow(block.T, cmap=cmap, norm=BoundaryNorm([-0.5, 0.5, 1.5], ncolors=2),
                  interpolation="nearest", aspect="auto")
        ax.set_yticks(np.arange(len(block.columns)), labels=block.columns, fontsize=7.4)
        ax.set_xticks(np.arange(len(block)), labels=block.index.astype(str), fontsize=6.4, rotation=90)
        ax.set_xticks(np.arange(len(block) + 1) - 0.5, minor=True)
        ax.set_yticks(np.arange(len(block.columns) + 1) - 0.5, minor=True)
        ax.grid(which="minor", color=GRID, lw=0.4)
        ax.tick_params(axis="both", which="both", length=0)
        ax.set_xlabel("Question number")
    axes[0, 0].legend(handles=[Patch(facecolor=c, edgecolor="#71808A", label=l)
                              for c, l in zip(colors, ["Correct", "Incorrect"])],
                      ncol=2, loc="lower center", bbox_to_anchor=(0.5, 1.01), frameon=False)
    save(fig, out / "figure4_errors.png")


def run(out: Path):
    out = Path(out)
    with plt.rc_context({"font.size": 9.5, "axes.spines.top": False, "axes.spines.right": False,
                         "axes.spines.left": False, "axes.axisbelow": True, "axes.edgecolor": GRID,
                         "text.color": DARK, "axes.labelcolor": DARK, "xtick.color": DARK, "ytick.color": DARK,
                         "ytick.major.size": 0}):
        accuracy_plot(out)
        primary_plot(out)
        marginals_plot(out)
        errors_plot(out)
