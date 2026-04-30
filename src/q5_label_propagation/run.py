from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import torch
import torch.nn.functional as F

from src.data_loader import largest_connected_component, load_facebook_mat
from src.q5_label_propagation.gcn import GCN, normalized_adjacency

SCHOOL = "Duke14"
ATTRS = ["dorm", "major", "year", "gender"]
FRACTIONS_HIDDEN = [0.10, 0.20, 0.30, 0.40]
ALL_ATTRS = ["status", "gender", "major", "dorm", "year"]

FIG_DIR = Path(__file__).resolve().parent.parent.parent / "figures" / "q5"
RESULTS_DIR = Path(__file__).resolve().parent.parent.parent / "results"


def features_excluding(G, nodes, target):
    feats = []
    for a in ALL_ATTRS:
        if a == target:
            continue
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


def label_vector(G, nodes, attr):
    raw = np.array([G.nodes[v].get(attr, 0) for v in nodes], dtype=int)
    valid = raw != 0
    classes = sorted(set(raw[valid].tolist()))
    idx = {c: i for i, c in enumerate(classes)}
    y = np.array([idx[r] if v else -1 for r, v in zip(raw, valid)], dtype=np.int64)
    return y, len(classes)


def split_indices(y, hidden_fraction, seed):
    rng = np.random.default_rng(seed)
    valid_idx = np.where(y >= 0)[0]
    rng.shuffle(valid_idx)
    n_hide = int(round(hidden_fraction * len(valid_idx)))
    test = valid_idx[:n_hide]
    rest = valid_idx[n_hide:]
    n_val = max(1, int(round(0.1 * len(rest))))
    val = rest[:n_val]
    train = rest[n_val:]
    return train, val, test


def train_gcn(G, attr, hidden_fraction, seed=0, epochs=200, hidden=64, patience=30):
    torch.manual_seed(seed)
    nodes = list(G.nodes())
    A_hat, _ = normalized_adjacency(G, nodes)
    X = features_excluding(G, nodes, attr)
    y_full, n_classes = label_vector(G, nodes, attr)
    train_idx, val_idx, test_idx = split_indices(y_full, hidden_fraction, seed)
    y_t = torch.tensor(y_full, dtype=torch.long)

    model = GCN(X.shape[1], hidden, n_classes)
    opt = torch.optim.Adam(model.parameters(), lr=1e-2, weight_decay=5e-4)

    best_val = -1.0
    best_state = None
    bad = 0
    for _ in range(epochs):
        model.train()
        out = model(X, A_hat)
        loss = F.cross_entropy(out[train_idx], y_t[train_idx])
        opt.zero_grad()
        loss.backward()
        opt.step()

        model.eval()
        with torch.no_grad():
            pred = model(X, A_hat).argmax(dim=1)
            val_acc = (pred[val_idx] == y_t[val_idx]).float().mean().item()
        if val_acc > best_val:
            best_val = val_acc
            best_state = {k: v.clone() for k, v in model.state_dict().items()}
            bad = 0
        else:
            bad += 1
            if bad >= patience:
                break

    model.load_state_dict(best_state)
    model.eval()
    with torch.no_grad():
        pred = model(X, A_hat).argmax(dim=1).numpy()

    accuracy = float((pred[test_idx] == y_full[test_idx]).mean())
    mae = float(np.abs(pred[test_idx] - y_full[test_idx]).mean())
    return {"accuracy": accuracy, "mae": mae}


def main():
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    G = largest_connected_component(load_facebook_mat(SCHOOL))

    rows = []
    for attr in ATTRS:
        for f in FRACTIONS_HIDDEN:
            res = train_gcn(G, attr, f, seed=0)
            print(f"{attr} f={f}: acc={res['accuracy']:.3f} mae={res['mae']:.2f}", flush=True)
            rows.append({"attr": attr, "hidden_fraction": f, **res})
    df = pd.DataFrame(rows)
    df.to_csv(RESULTS_DIR / "q5_label_propagation.csv", index=False)

    fig, ax = plt.subplots(figsize=(7, 4.5))
    for attr in ATTRS:
        sub = df[df["attr"] == attr]
        ax.plot(sub["hidden_fraction"], sub["accuracy"], marker="o", label=attr)
    ax.set_xlabel("fraction de labels masqués")
    ax.set_ylabel("accuracy")
    ax.set_title(f"GCN label propagation — {SCHOOL}")
    ax.legend()
    fig.tight_layout()
    fig.savefig(FIG_DIR / "accuracy_vs_hidden.png", dpi=150)
    plt.close(fig)


if __name__ == "__main__":
    main()
