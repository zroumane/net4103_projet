import math

from src.q4_link_prediction.base import LinkPrediction


class CommonNeighbors(LinkPrediction):
    def __init__(self, graph):
        super().__init__(graph)
        self._neigh = {}

    def fit(self):
        # on précalcule les voisinages en set pour des intersections rapides
        self._neigh = {v: set(self.graph.neighbors(v)) for v in self.graph.nodes()}
        return self

    def predict(self, u, v):
        return float(len(self._neigh[u] & self._neigh[v]))


class Jaccard(LinkPrediction):
    def __init__(self, graph):
        super().__init__(graph)
        self._neigh = {}

    def fit(self):
        self._neigh = {v: set(self.graph.neighbors(v)) for v in self.graph.nodes()}
        return self

    def predict(self, u, v):
        nu, nv = self._neigh[u], self._neigh[v]
        union = nu | nv
        if not union:
            return 0.0
        return len(nu & nv) / len(union)


class AdamicAdar(LinkPrediction):
    def __init__(self, graph):
        super().__init__(graph)
        self._neigh = {}
        self._inv_log_deg = {}

    def fit(self):
        self._neigh = {v: set(self.graph.neighbors(v)) for v in self.graph.nodes()}
        # 1/log(deg) précalculé ; les nœuds de degré 1 (log 1 = 0) sont neutralisés
        self._inv_log_deg = {
            v: (1.0 / math.log(len(neigh)) if len(neigh) > 1 else 0.0)
            for v, neigh in self._neigh.items()
        }
        return self

    def predict(self, u, v):
        common = self._neigh[u] & self._neigh[v]
        return sum(self._inv_log_deg[w] for w in common)
