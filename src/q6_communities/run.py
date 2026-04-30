from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from networkx.algorithms.community import (
    label_propagation_communities,
    louvain_communities,
    modularity,
)
from sklearn.metrics import adjusted_rand_score, normalized_mutual_info_score

from src.data_loader import largest_connected_component, load_facebook_mat


SCHOOLS = ["Caltech36", "Reed98", "Haverford76", "Smith60", "JohnsHopkins55"]
ATTRS = ["dorm", "year", "major"]

FIG_DIR = Path(__file__).resolve().parent.parent.parent / "figures" / "q6"
RESULTS_DIR = Path(__file__).resolve().parent.parent.parent / "results"


def communities_to_labels(comms, nodes):
    label = {}
    for i, c in enumerate(comms):
        for v in c:
            label[v] = i
    return np.array([label[v] for v in nodes])


def attribute_labels(G, nodes, attr):
    raw = np.array([G.nodes[v].get(attr, 0) for v in nodes], dtype=int)
    valid = raw != 0
    return raw, valid


def detect(G, algo):
    if algo == "Louvain":
        return louvain_communities(G, seed=0)
    return list(label_propagation_communities(G))


def run_school(school):
    G = largest_connected_component(load_facebook_mat(school))
    nodes = list(G.nodes())

    rows = []
    for algo in ["Louvain", "LabelProp"]:
        comms = detect(G, algo)
        comm_labels = communities_to_labels(comms, nodes)
        mod = modularity(G, comms)
        for attr in ATTRS:
            attr_lbl, valid = attribute_labels(G, nodes, attr)
            if valid.sum() < 10:
                continue
            nmi = normalized_mutual_info_score(attr_lbl[valid], comm_labels[valid])
            ari = adjusted_rand_score(attr_lbl[valid], comm_labels[valid])
            rows.append({
                "school": school, "algo": algo, "attr": attr,
                "n_communities": len(comms), "modularity": mod,
                "nmi": nmi, "ari": ari,
            })
            print(f"{school} {algo} vs {attr}: NMI={nmi:.3f} ARI={ari:.3f}", flush=True)
    return rows


def main():
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    all_rows = []
    for s in SCHOOLS:
        all_rows.extend(run_school(s))
        pd.DataFrame(all_rows).to_csv(RESULTS_DIR / "q6_communities.csv", index=False)

    df = pd.DataFrame(all_rows)
    for metric in ["nmi", "ari"]:
        fig, ax = plt.subplots(figsize=(8, 4.5))
        pivot = df.pivot_table(index="school", columns=["algo", "attr"], values=metric)
        pivot.plot(kind="bar", ax=ax)
        ax.set_ylabel(metric.upper())
        ax.set_title(f"{metric.upper()} entre communautés détectées et attributs")
        ax.legend(loc="upper right", fontsize=8)
        fig.tight_layout()
        fig.savefig(FIG_DIR / f"{metric}_by_school.png", dpi=150)
        plt.close(fig)


if __name__ == "__main__":
    main()
