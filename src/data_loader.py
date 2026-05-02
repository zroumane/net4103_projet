from pathlib import Path

import networkx as nx

# attributs Facebook100. Les .gml utilisent student_fac/major_index ;
# on remappe vers les noms historiques pour rester cohérent avec le code existant.
GML_ATTR_RENAME = {
    "student_fac": "status",
    "major_index": "major",
}

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


def load_facebook_school(school, data_dir=DATA_DIR):
    G = nx.read_gml(str(data_dir / f"{school}.gml"), label="id")
    G.graph["name"] = school

    for n, data in G.nodes(data=True):
        data.pop("label", None)
        for old, new in GML_ATTR_RENAME.items():
            if old in data:
                data[new] = data.pop(old)

    return G


# alias pour ne pas casser les imports existants
load_facebook_mat = load_facebook_school


def largest_connected_component(G):
    nodes = max(nx.connected_components(G), key=len)
    H = G.subgraph(nodes).copy()
    H.graph["name"] = G.graph.get("name", "") + "_LCC"
    return H


def list_available_schools(data_dir=DATA_DIR):
    if not data_dir.exists():
        return []
    return sorted(p.stem for p in data_dir.glob("*.gml"))
