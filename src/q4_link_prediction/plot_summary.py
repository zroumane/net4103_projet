from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from src.q4_link_prediction.run import FIG_DIR, RESULTS_DIR, plot_per_metric


def plot_summary(df):
    # courbe agrégée : precision@k moyennée sur les écoles, une courbe par métrique,
    # un panel par fraction retirée
    fractions = sorted(df["fraction_removed"].unique())
    metrics = sorted(df["metric"].unique())

    fig, axes = plt.subplots(1, len(fractions), figsize=(5 * len(fractions), 4), sharey=True)
    for ax, f in zip(axes, fractions):
        sub = df[df["fraction_removed"] == f]
        for metric in metrics:
            m = sub[sub["metric"] == metric].groupby("k")["precision_at_k"].mean()
            ax.plot(m.index, m.values, marker="o", label=metric)
        ax.set_title(f"f = {f}")
        ax.set_xlabel("k")
        ax.legend()
    axes[0].set_ylabel("precision@k (moyenne sur écoles)")
    fig.suptitle("Comparaison des trois métriques — moyenne sur les écoles")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "summary_precision_at_k.png", dpi=150)
    plt.close(fig)


def main():
    df = pd.read_csv(RESULTS_DIR / "q4_link_prediction.csv")
    Path(FIG_DIR).mkdir(parents=True, exist_ok=True)
    for school in df["school"].unique():
        plot_per_metric(df, school)
    plot_summary(df)


if __name__ == "__main__":
    main()
