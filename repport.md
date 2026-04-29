# NET 4103 — Network Science and Graph Learning

## Question 2

Tout est calculé sur le LCC, puisque les tailles données dans l'énoncé (762, 6402, 5157) sont celles du LCC.

### 2a

| école | n | m | densité | C global | ⟨C local⟩ |
|---|---|---|---|---|---|
| Caltech36 | 762 | 16 651 | 0.0574 | 0.291 | 0.409 |
| MIT8 | 6 402 | 251 230 | 0.0123 | 0.180 | 0.272 |
| JohnsHopkins55 | 5 157 | 186 572 | 0.0140 | 0.193 | 0.269 |

![Distribution des degrés](figures/q2/degree_distribution.png)

Les trois réseaux sont sparses : la densité monte à 5.7 % pour Caltech (le plus petit) mais tombe en dessous de 1.5 % pour MIT et Johns Hopkins. C'est cohérent avec ce qu'on attend d'un graphe social — chaque utilisateur n'a de lien qu'avec une petite fraction des autres membres de son université.

Les coefficients de clustering sont en revanche très élevés par rapport à ceux d'un graphe aléatoire de même densité : le clustering local moyen vaut environ 7× la densité pour Caltech, 22× pour MIT, 19× pour Johns Hopkins. Combiné à la faible densité, ça donne la signature classique d'un réseau small-world : les amis de mes amis sont très souvent eux-mêmes liés, ce qui correspond à de fortes communautés locales (promos, dorms, départements).

Le clustering global (transitivité) est plus bas que le clustering local moyen sur les trois graphes. C'est typique des graphes hétérogènes en degré : les hubs ont beaucoup de triplets ouverts qui ne se ferment pas et tirent la transitivité globale vers le bas, tandis que la moyenne des C(v) est dominée par les nombreux nœuds de petit degré qui appartiennent à des cliques.

### 2b

![Degré vs clustering local](figures/q2/degree_vs_clustering.png)

Sur les trois graphes, C(v) décroît avec k, à peu près en 1/k sur deux ordres de grandeur. Ça suggère une organisation hiérarchique : les nœuds peu connectés appartiennent à des cliques denses, tandis que les hubs connectent plusieurs cliques différentes et ont donc proportionnellement moins de triangles fermés.

Caltech se distingue très nettement : densité et clustering local moyen 4 à 5× plus élevés que les deux autres. C'est cohérent avec le fait que Caltech est le plus petit campus du dataset, avec une vie sociale très structurée par les *house systems* qui jouent le rôle des dorms. MIT et Johns Hopkins se ressemblent davantage entre eux : populations comparables, structures comparables.

## Question 3

Calcul effectué sur le LCC de chaque graphe, pour les 100 graphes du dataset. Pour les attributs catégoriels (status, major, dorm, gender) j'utilise l'assortativité de Newman ; pour le degré c'est le coefficient de Pearson sur les degrés des extrémités. Avant le calcul je retire les nœuds dont l'attribut vaut 0 (= manquant dans Facebook100), sinon « manquant » est traité comme une catégorie à part entière, ce qui biaise le résultat.

| attribut | moyenne | médiane | min | max | % > 0 |
|---|---|---|---|---|---|
| status | 0.323 | 0.317 | 0.110 | 0.543 | 100 % |
| dorm | 0.227 | 0.221 | 0.079 | 0.485 | 100 % |
| degree | 0.063 | 0.065 | -0.066 | 0.197 | 89 % |
| major | 0.056 | 0.050 | 0.030 | 0.151 | 100 % |
| gender | 0.053 | 0.055 | -0.092 | 0.246 | 89 % |

![status](figures/q3/assortativity_status.png)

Le statut (étudiant / faculty / staff / alumni) est de loin l'attribut le plus assortatif : moyenne de 0.32, jamais en dessous de 0.11. Les étudiants se lient massivement entre eux, les alumni entre eux, le personnel entre lui. C'est attendu : ces catégories correspondent à des étapes différentes du parcours et fréquentent les mêmes lieux et les mêmes cohortes, et leurs interactions inter-groupes sont rares en 2005.

![dorm](figures/q3/assortativity_dorm.png)

Le dorm arrive en deuxième position avec une moyenne de 0.23 et des valeurs jusqu'à 0.48. Toujours positif. La cohabitation est un générateur d'amitiés très efficace en première année — on partage l'espace, les repas, les soirées — et ces liens se cristallisent rapidement sur Facebook. L'amplitude des valeurs (entre 0.08 et 0.48) reflète probablement la diversité des organisations résidentielles : les universités où les dorms sont thématiques ou par promotion ont une assortativité plus élevée que celles où le placement est plus aléatoire.

![degree](figures/q3/assortativity_degree.png)

L'assortativité de degré est légèrement positive en moyenne (0.06) mais avec une variance importante : 89 % des graphes sont positifs, mais 11 % sont dissortatifs. C'est typique des réseaux sociaux (par opposition aux réseaux technologiques qui sont franchement dissortatifs), avec un effet modéré : les hubs gardent un certain nombre d'amis peu connectés.

![major](figures/q3/assortativity_major.png)

Le major est positif partout mais avec une amplitude faible (0.03 à 0.15, moyenne 0.06). Les étudiants d'un même département se croisent en cours et en TP, ce qui crée une homophilie réelle, mais beaucoup d'amitiés se forment via la résidence et la promotion, où les majors se mélangent.

![gender](figures/q3/assortativity_gender.png)

Le gender est l'attribut le moins assortatif : moyenne de 0.053, distribution centrée près de 0, avec quelques universités franchement positives et quelques-unes négatives (jusqu'à -0.09). Comme le sujet le suggère, la faible amplitude indique que le genre n'est pas un facteur structurant majeur des amitiés Facebook : on parle d'une faible homophilie globale, pas d'une ségrégation. Les valeurs négatives correspondent vraisemblablement à des universités où la dynamique de couples hétéro influence les liens d'amitié visibles.

L'ordre observé `status > dorm > degree ≈ major ≈ gender` est cohérent avec ce que rapportent Traud *et al.* Les deux processus qui dominent l'amitié sur Facebook 2005 sont l'appartenance au même groupe institutionnel (statut) et la cohabitation (dorm), très loin devant les homophilies plus douces comme le major ou le genre.

## Question 4

### 4b

J'ai écrit la classe abstraite `LinkPrediction` (en suivant le listing 1 du sujet) dans [src/q4_link_prediction/base.py](src/q4_link_prediction/base.py), puis les trois métriques dans [src/q4_link_prediction/metrics.py](src/q4_link_prediction/metrics.py).

Pour chaque prédicteur, `fit` précalcule les voisinages comme des `set` Python : ça permet de faire les intersections en O(min(|Γ(u)|, |Γ(v)|)) au lieu de retraverser le graphe networkx à chaque appel. Pour Adamic-Adar je précalcule aussi `1/log(deg(w))` pour chaque nœud, comme ça `predict` se résume à une somme sur les voisins communs.

Définitions :

- Common Neighbors : `score(u,v) = |Γ(u) ∩ Γ(v)|`
- Jaccard : `|Γ(u) ∩ Γ(v)| / |Γ(u) ∪ Γ(v)|`
- Adamic / Adar : `Σ_{w ∈ Γ(u) ∩ Γ(v)} 1 / log|Γ(w)|`

### 4c

Code dans [src/q4_link_prediction/evaluation.py](src/q4_link_prediction/evaluation.py) et [run.py](src/q4_link_prediction/run.py). Le protocole est celui de l'énoncé :

1. retirer aléatoirement une fraction `f` des arêtes (`f ∈ {0.05, 0.10, 0.15, 0.20}`),
2. entraîner le prédicteur sur le graphe résiduel,
3. scorer chaque paire de non-arêtes,
4. trier par score décroissant et garder le top-k,
5. comparer au set des arêtes retirées pour calculer top@k, precision@k et recall@k pour `k ∈ {50, 100, 150, 200, 250, 300, 350, 400}`.

L'énoncé demande d'itérer sur toutes les paires `|V|×|V|`. Pour Common Neighbors, Jaccard et Adamic-Adar, les paires sans aucun voisin commun ont un score nul et ne peuvent jamais entrer dans le top-k. J'énumère donc uniquement les paires (u, v) partageant au moins un voisin (= les chemins de longueur 2), ce qui rend traitables les graphes plus gros sans changer le résultat du top@k.

`precision@k` et `top@k` sont identiques par construction (le top-k contient k éléments donc TP+FP = k, d'où TP/k = TP/(TP+FP)). Je rapporte les deux pour rester fidèle à l'énoncé.

J'ai lancé le protocole sur 12 écoles de tailles modérées (Caltech, Reed, Simmons, Haverford, Swarthmore, Amherst, Bowdoin, Wesleyan, Oberlin, Smith, Hamilton, Mich67) ; je présente les résultats agrégés ci-dessous, puis quelques exemples par école.

![Comparaison agrégée](figures/q4/summary_precision_at_k.png)

Les trois métriques se classent de façon stable : Adamic-Adar et Common Neighbors font à peu près jeu égal et largement au-dessus de Jaccard. Le tableau suivant donne la moyenne de precision@k=100 sur les 12 écoles :

| f retiré | CommonNeighbors | Jaccard | AdamicAdar |
|---|---|---|---|
| 0.05 | 0.42 | 0.35 | 0.44 |
| 0.10 | 0.61 | 0.49 | 0.63 |
| 0.15 | 0.72 | 0.57 | 0.73 |
| 0.20 | 0.77 | 0.59 | 0.78 |

On voit aussi que la precision@k augmente avec la fraction retirée. C'est attendu : à f=0.05 il y a peu d'arêtes à retrouver, donc la chance qu'une paire bien notée par la métrique soit effectivement dans `E_removed` est plus faible (beaucoup des paires bien notées correspondent à des arêtes du graphe d'origine qui n'ont pas été retirées). À f=0.20 il y a quatre fois plus d'arêtes à retrouver et la même paire candidate a quatre fois plus de chances de tomber juste.

Côté courbes par école, deux exemples typiques :

![Caltech precision@k](figures/q4/precision_at_k_Caltech36.png)

![Mich67 precision@k](figures/q4/precision_at_k_Mich67.png)

La precision décroît avec k : les premières paires du top-k sont les plus sûres et la qualité s'érode quand on descend dans le classement, ce qui est la sémantique normale d'un classement par score.

Reed98 est l'école sur laquelle les trois métriques sont les moins performantes (precision@100 autour de 0.20 à f=0.05). Reed est aussi parmi les plus petits réseaux du dataset : moins de voisins communs disponibles, donc moins de signal pour ces métriques topologiques pures.

Côté recall, les valeurs restent faibles parce que k est petit devant le nombre d'arêtes retirées. Sur les écoles les plus grandes (par exemple Mich67 avec plusieurs milliers d'arêtes retirées à f=0.05), 100 prédictions correctes ne représentent qu'environ 1 % des arêtes à retrouver. Le tableau ci-dessous donne le recall@400 moyen :

| f retiré | CommonNeighbors | Jaccard | AdamicAdar |
|---|---|---|---|
| 0.05 | 0.040 | 0.044 | 0.042 |
| 0.10 | 0.035 | 0.034 | 0.036 |
| 0.15 | 0.030 | 0.028 | 0.031 |
| 0.20 | 0.025 | 0.023 | 0.026 |

Le recall décroît avec f parce que `|E_removed|` augmente proportionnellement, alors que k reste fixé à 400. Pour interpréter le compromis precision / recall, c'est plus parlant de regarder precision et recall ensemble : à f=0.20 par exemple, Adamic-Adar atteint 78 % de precision@100 mais ne récupère que 2.6 % des arêtes retirées avec ses 400 meilleures prédictions.
