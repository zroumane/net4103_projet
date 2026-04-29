from pathlib import Path

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd

from src.data_loader import (
    DATA_DIR,
    largest_connected_component,
    list_available_schools,
    load_facebook_mat,
)

CATEGORICAL_ATTRS = ["status", "major", "dorm", "gender"]
FIG_DIR = Path(__file__).resolve().parent.parent / "figures" / "q3"
RESULTS_DIR = Path(__file__).resolve().parent.parent / "results"


def filter_missing(G, attr):
    # dans Facebook100 les attributs manquants valent 0
    keep = [v for v, val in G.nodes(data=attr) if val and val != 0]
    return G.subgraph(keep)


def assortativity_one_graph(G):
    out = {"name": G.graph.get("name", ""), "n": G.number_of_nodes()}
    for attr in CATEGORICAL_ATTRS:
        H = filter_missing(G, attr)
        if H.number_of_edges() == 0:
            out[attr] = np.nan
            continue
        try:
            out[attr] = nx.attribute_assortativity_coefficient(H, attr)
        except (ValueError, ZeroDivisionError):
            out[attr] = np.nan
    try:
        out["degree"] = nx.degree_assortativity_coefficient(G)
    except (ValueError, ZeroDivisionError):
        out["degree"] = np.nan
    return out


def compute_all(data_dir=DATA_DIR, checkpoint=None):
    rows = []
    for school in list_available_schools(data_dir):
        G = largest_connected_component(load_facebook_mat(school, data_dir))
        rows.append(assortativity_one_graph(G))
        print(f"done: {school} (n={G.number_of_nodes()})", flush=True)
        if checkpoint is not None:
            pd.DataFrame(rows).to_csv(checkpoint, index=False)
    return pd.DataFrame(rows)


def plot_attribute(df, attr):
    fig, (ax_scatter, ax_hist) = plt.subplots(1, 2, figsize=(11, 4))
    values = df[attr].dropna()

    ax_scatter.scatter(df["n"], df[attr], s=20, alpha=0.7)
    ax_scatter.axhline(0, color="black", linestyle="--", linewidth=1)
    ax_scatter.set_xscale("log")
    ax_scatter.set_xlabel("taille du réseau n (LCC)")
    ax_scatter.set_ylabel(f"assortativité — {attr}")
    ax_scatter.set_title(f"{attr} — scatter")

    ax_hist.hist(values, bins=20, alpha=0.75, edgecolor="black")
    ax_hist.axvline(0, color="black", linestyle="--", linewidth=1)
    ax_hist.set_xlabel(f"assortativité — {attr}")
    ax_hist.set_ylabel("nb. de réseaux")
    ax_hist.set_title(f"{attr} — distribution (moyenne = {values.mean():.3f})")

    fig.tight_layout()
    fig.savefig(FIG_DIR / f"assortativity_{attr}.png", dpi=150)
    plt.close(fig)


def main():
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    df = compute_all(checkpoint=RESULTS_DIR / "assortativity.csv")
    df.to_csv(RESULTS_DIR / "assortativity.csv", index=False)

    for attr in CATEGORICAL_ATTRS + ["degree"]:
        plot_attribute(df, attr)

    print("\nMoyenne par attribut :")
    print(df[CATEGORICAL_ATTRS + ["degree"]].mean().round(4))


if __name__ == "__main__":
    main()
