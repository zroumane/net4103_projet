import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

from src.q4_link_prediction.base import LinkPrediction

ATTRS = ["status", "gender", "major", "dorm", "year"]


def normalized_adjacency(G, nodes):
    n = len(nodes)
    idx = {v: i for i, v in enumerate(nodes)}
    A = torch.zeros((n, n))
    for u, v in G.edges():
        i, j = idx[u], idx[v]
        A[i, j] = 1.0
        A[j, i] = 1.0
    A = A + torch.eye(n)
    deg = A.sum(dim=1)
    d_inv_sqrt = deg.pow(-0.5)
    return d_inv_sqrt.unsqueeze(1) * A * d_inv_sqrt.unsqueeze(0), idx


def node_features(G, nodes):
    feats = []
    for a in ATTRS:
        vals = [G.nodes[v].get(a, 0) for v in nodes]
        uniq = sorted(set(vals))
        col = {x: i for i, x in enumerate(uniq)}
        oh = np.zeros((len(nodes), len(uniq)), dtype=np.float32)
        for i, x in enumerate(vals):
            oh[i, col[x]] = 1.0
        feats.append(oh)
    deg = np.array([G.degree(v) for v in nodes], dtype=np.float32)
    deg = (deg - deg.mean()) / (deg.std() + 1e-6)
    feats.append(deg.reshape(-1, 1))
    return torch.tensor(np.concatenate(feats, axis=1), dtype=torch.float32)


def sample_negatives(n, n_pos, pos_set, rng):
    neg = set()
    while len(neg) < n_pos:
        i = int(rng.integers(0, n))
        j = int(rng.integers(0, n))
        if i == j:
            continue
        a, b = (i, j) if i < j else (j, i)
        if (a, b) in pos_set or (a, b) in neg:
            continue
        neg.add((a, b))
    return list(neg)


class GCN(nn.Module):
    def __init__(self, d_in, d_hidden, d_out, dropout=0.5):
        super().__init__()
        self.lin1 = nn.Linear(d_in, d_hidden)
        self.lin2 = nn.Linear(d_hidden, d_out)
        self.dropout = dropout

    def forward(self, x, A_hat):
        h = F.relu(A_hat @ self.lin1(x))
        h = F.dropout(h, p=self.dropout, training=self.training)
        return A_hat @ self.lin2(h)


class GCNLinkPredictor(LinkPrediction):
    def __init__(self, graph, hidden=64, embed=32, epochs=100, seed=0):
        super().__init__(graph)
        self.hidden = hidden
        self.embed = embed
        self.epochs = epochs
        self.seed = seed

    def fit(self):
        torch.manual_seed(self.seed)
        rng = np.random.default_rng(self.seed)

        nodes = list(self.graph.nodes())
        A_hat, idx = normalized_adjacency(self.graph, nodes)
        X = node_features(self.graph, nodes)

        pos_set = set()
        for u, v in self.graph.edges():
            i, j = idx[u], idx[v]
            pos_set.add((i, j) if i < j else (j, i))
        pos_edges = list(pos_set)
        n = len(nodes)

        model = GCN(X.shape[1], self.hidden, self.embed)
        opt = torch.optim.Adam(model.parameters(), lr=1e-2, weight_decay=5e-4)
        pos_t = torch.tensor(pos_edges, dtype=torch.long)

        for _ in range(self.epochs):
            model.train()
            neg_edges = sample_negatives(n, len(pos_edges), pos_set, rng)
            neg_t = torch.tensor(neg_edges, dtype=torch.long)

            z = model(X, A_hat)
            s_pos = (z[pos_t[:, 0]] * z[pos_t[:, 1]]).sum(dim=1)
            s_neg = (z[neg_t[:, 0]] * z[neg_t[:, 1]]).sum(dim=1)

            logits = torch.cat([s_pos, s_neg])
            labels = torch.cat([torch.ones_like(s_pos), torch.zeros_like(s_neg)])
            loss = F.binary_cross_entropy_with_logits(logits, labels)

            opt.zero_grad()
            loss.backward()
            opt.step()

        model.eval()
        with torch.no_grad():
            self.z = model(X, A_hat).numpy()
        self.idx = idx
        return self

    def predict(self, u, v):
        i, j = self.idx[u], self.idx[v]
        return float(np.dot(self.z[i], self.z[j]))
