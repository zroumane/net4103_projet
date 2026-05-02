# NET 4103 — Analyse de Facebook100

Projet de fin de module : analyse structurelle, prédiction de liens et propagation de labels sur le dataset Facebook100.

## Installation

Pré-requis : [`uv`](https://docs.astral.sh/uv/).

```bash
uv sync
```

Le dataset doit être placé dans `data/` au format `.gml` (un fichier par école, ex. `Caltech36.gml`).

## Lancer les expériences

Toutes les commandes depuis la racine du projet :

```bash
uv run python main.py q2    # densité, clustering, distribution des degrés
uv run python main.py q3    # assortativité sur les 100 graphes (~30 min)
uv run python main.py q4    # link prediction CN / Jaccard / AA (12 écoles)
uv run python main.py q4e   # link prediction par GCN (5 écoles)
uv run python main.py q5    # propagation de labels par GCN (Duke14)
uv run python main.py q6    # détection de communautés (Louvain, LabelProp)
```

Les résultats sont écrits dans `results/` (CSV) et `figures/` (PNG).

## Rapport

```bash
bash render.sh
```

Demande le nom de l'auteur et produit `output.pdf` à partir de `repport.md` via pandoc + xelatex.
