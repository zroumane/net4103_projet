from pathlib import Path

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd

from src.data_loader import largest_connected_component, load_facebook_mat

SCHOOLS = ["Caltech36", "MIT8", "JohnsHopkins55"]
FIG_DIR = Path(__file__).resolve().parent.parent / "figures" / "q2"
RESULTS_DIR = Path(__file__).resolve().parent.parent / "results"


def basic_stats(G):
    return {
        "n": G.number_of_nodes(),
        "m": G.number_of_edges(),
        "density": nx.density(G),
        "global_clustering": nx.transitivity(G),
        "mean_local_clustering": nx.average_clustering(G),
    }


def plot_degree_distribution(G, ax):
    degrees = np.array([d for _, d in G.degree()])
    bins = np.logspace(0, np.log10(degrees.max() + 1), 40)
    ax.hist(degrees, bins=bins, alpha=0.75, edgecolor="black")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("degré k")
    ax.set_ylabel("nb. de nœuds")
    ax.set_title(f"{G.graph['name']} (n={G.number_of_nodes()})")


def plot_degree_vs_clustering(G, ax):
    clustering = nx.clustering(G)
    degrees = dict(G.degree())
    xs = [degrees[v] for v in G.nodes()]
    ys = [clustering[v] for v in G.nodes()]
    ax.scatter(xs, ys, s=6, alpha=0.3)
    ax.set_xscale("log")
    ax.set_xlabel("degré k")
    ax.set_ylabel("clustering local C(v)")
    ax.set_title(G.graph["name"])


def main():
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    graphs = {school: largest_connected_component(load_facebook_mat(school)) for school in SCHOOLS}

    rows = []
    print(f"{'school':<20}{'n':>8}{'m':>10}{'density':>12}{'C_global':>12}{'<C_local>':>12}")
    for school, G in graphs.items():
        s = basic_stats(G)
        rows.append({"school": school, **s})
        print(
            f"{school:<20}{s['n']:>8}{s['m']:>10}{s['density']:>12.5f}"
            f"{s['global_clustering']:>12.4f}{s['mean_local_clustering']:>12.4f}"
        )
    pd.DataFrame(rows).to_csv(RESULTS_DIR / "q2_stats.csv", index=False)

    fig, axes = plt.subplots(1, 3, figsize=(15, 4))
    for ax, (_, G) in zip(axes, graphs.items()):
        plot_degree_distribution(G, ax)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "degree_distribution.png", dpi=150)
    plt.close(fig)

    fig, axes = plt.subplots(1, 3, figsize=(15, 4))
    for ax, (_, G) in zip(axes, graphs.items()):
        plot_degree_vs_clustering(G, ax)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "degree_vs_clustering.png", dpi=150)
    plt.close(fig)


if __name__ == "__main__":
    main()
