import torch
import torch.nn as nn
import torch.nn.functional as F


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


class GCN(nn.Module):
    def __init__(self, d_in, d_hidden, n_classes, dropout=0.5):
        super().__init__()
        self.lin1 = nn.Linear(d_in, d_hidden)
        self.lin2 = nn.Linear(d_hidden, n_classes)
        self.dropout = dropout

    def forward(self, x, A_hat):
        h = F.relu(A_hat @ self.lin1(x))
        h = F.dropout(h, p=self.dropout, training=self.training)
        return A_hat @ self.lin2(h)
