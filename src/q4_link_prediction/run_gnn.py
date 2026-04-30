from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from src.data_loader import largest_connected_component, load_facebook_mat
from src.q4_link_prediction.evaluation import evaluate
from src.q4_link_prediction.gnn import GCNLinkPredictor
from src.q4_link_prediction.metrics import AdamicAdar, CommonNeighbors, Jaccard

FRACTIONS = [0.05, 0.10, 0.15, 0.20]
KS = [50, 100, 150, 200, 250, 300, 350, 400]

FIG_DIR = Path(__file__).resolve().parent.parent.parent / "figures" / "q4"
RESULTS_DIR = Path(__file__).resolve().parent.parent.parent / "results"


def run_on_school(school, seed=0):
    G = largest_connected_component(load_facebook_mat(school))
    rows = []
    for cls in [CommonNeighbors, Jaccard, AdamicAdar, GCNLinkPredictor]:
        for r in evaluate(cls, G, FRACTIONS, KS, seed=seed):
            rows.append({"school": school, **r.__dict__})
    return pd.DataFrame(rows)


def plot_compare(df, school):
    sub = df[df["school"] == school]
    metrics = sorted(sub["metric"].unique())
    fig, axes = plt.subplots(1, len(metrics), figsize=(5 * len(metrics), 4), sharey=True)
    for ax, metric in zip(axes, metrics):
        m = sub[sub["metric"] == metric]
        for f, g in m.groupby("fraction_removed"):
            ax.plot(g["k"], g["precision_at_k"], marker="o", label=f"f={f}")
        ax.set_title(metric)
        ax.set_xlabel("k")
        ax.set_ylabel("precision@k")
        ax.legend()
    fig.suptitle(f"{school} — link prediction (avec GCN)")
    fig.tight_layout()
    fig.savefig(FIG_DIR / f"gnn_precision_at_k_{school}.png", dpi=150)
    plt.close(fig)


def main():
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    schools = ["Caltech36", "Reed98", "Haverford76", "Simmons81", "Swarthmore42"]
    dfs = []
    for s in schools:
        d = run_on_school(s)
        dfs.append(d)
        pd.concat(dfs, ignore_index=True).to_csv(
            RESULTS_DIR / "q4e_gnn_link_prediction.csv", index=False
        )
        plot_compare(pd.concat(dfs, ignore_index=True), s)


if __name__ == "__main__":
    main()
