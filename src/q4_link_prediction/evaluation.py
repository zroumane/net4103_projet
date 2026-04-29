from dataclasses import dataclass

import numpy as np


@dataclass
class EvalResult:
    metric: str
    fraction_removed: float
    k: int
    top_at_k: float
    precision_at_k: float
    recall_at_k: float


def remove_random_edges(G, fraction, rng):
    edges = list(G.edges())
    n_remove = int(round(fraction * len(edges)))
    idx = rng.choice(len(edges), size=n_remove, replace=False)
    removed = {tuple(sorted(edges[i])) for i in idx}
    H = G.copy()
    H.remove_edges_from(removed)
    return H, removed


def candidate_pairs(G):
    # on ne considère que les paires (u, v) avec au moins un voisin commun :
    # pour CN/Jaccard/AA toutes les autres paires ont un score nul donc
    # ne changeront pas le top@k. Ça évite d'énumérer |V|^2 paires.
    seen = set()
    for w in G.nodes():
        nbrs = list(G.neighbors(w))
        for i in range(len(nbrs)):
            for j in range(i + 1, len(nbrs)):
                u, v = nbrs[i], nbrs[j]
                pair = (u, v) if u < v else (v, u)
                if pair in seen or G.has_edge(u, v):
                    continue
                seen.add(pair)
                yield pair


def score_all_pairs(predictor, pairs):
    return [(pair, predictor.predict(*pair)) for pair in pairs]


def evaluate(predictor_cls, G, fractions, ks, seed=0):
    rng = np.random.default_rng(seed)
    results = []
    for f in fractions:
        H, removed = remove_random_edges(G, f, rng)
        predictor = predictor_cls(H).fit()

        scored = score_all_pairs(predictor, candidate_pairs(H))
        scored.sort(key=lambda x: x[1], reverse=True)

        for k in ks:
            top_k = scored[:k]
            tp = sum(1 for pair, _ in top_k if pair in removed)
            top_at_k = tp / k if k > 0 else 0.0
            recall_at_k = tp / len(removed) if removed else 0.0

            results.append(
                EvalResult(
                    metric=predictor_cls.__name__,
                    fraction_removed=f,
                    k=k,
                    top_at_k=top_at_k,
                    precision_at_k=top_at_k,
                    recall_at_k=recall_at_k,
                )
            )
    return results
