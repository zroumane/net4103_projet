from pathlib import Path

import networkx as nx
import numpy as np
from scipy.io import loadmat

# colonnes de local_info dans les .mat Facebook100
ATTR_NAMES = [
    "status",
    "gender",
    "major",
    "second_major",
    "dorm",
    "year",
    "high_school",
]

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def load_facebook_mat(school, data_dir=DATA_DIR):
    mat = loadmat(str(data_dir / f"{school}.mat"))
    A = mat["A"]
    local_info = np.asarray(mat["local_info"], dtype=int)

    G = nx.from_scipy_sparse_array(A)
    G.graph["name"] = school

    for i, attr in enumerate(ATTR_NAMES):
        nx.set_node_attributes(G, dict(enumerate(local_info[:, i].tolist())), name=attr)

    return G


def largest_connected_component(G):
    nodes = max(nx.connected_components(G), key=len)
    H = G.subgraph(nodes).copy()
    H.graph["name"] = G.graph.get("name", "") + "_LCC"
    return H


def list_available_schools(data_dir=DATA_DIR):
    if not data_dir.exists():
        return []
    return sorted(p.stem for p in data_dir.glob("*.mat"))
