"""
Módulo: clustering.py

Descripción:
    Ejecuta los 3 algoritmos de clustering (Greedy Modularity, Edge Betweenness
    e Infomap) sobre una red STRING previamente generada con generar_red.py.
    Produce gráficos y archivos JSON con los resultados de cada método.

Entrada:
    results/redes/<modo>_score<score>/red_<modo>_score<score>.txt

Salida:
    results/redes/<modo>_score<score>/clustering/
        └── <algoritmo>/
                ├── <algoritmo>_<modo>_score<score>.png
                └── <algoritmo>_<modo>_score<score>.json

Contenido de cada JSON:
    {
        "algorithm": str,
        "modularity" | "best_modularity" | "codelength": float,
        "communities": list[list[str]],
        "modularity_trace": list[float] (solo Edge Betweenness)
    }

Propósito:
    Este módulo debe ser invocado desde pipeline.py
    mediante la función pública:

        ejecutar_clustering(modo, score)

    Los resultados generados sirven para análisis comparativos entre
    métodos de clustering y para caracterizar la estructura modular
    de cada red antes de análisis funcionales posteriores.
"""

import json
from pathlib import Path

import matplotlib.pyplot as plt
import networkx as nx
from infomap import Infomap
from networkx.algorithms.community import greedy_modularity_communities
from networkx.algorithms.community.quality import modularity

from paths import RESULTADOS_DIR


# ============================================================
# RUTAS
# ============================================================

def preparar_rutas(modo: str, score: int):
    base_dir = RESULTADOS_DIR / "redes" / f"{modo}_score{score}"
    clustering_dir = base_dir / "clustering"

    greedy_dir = clustering_dir / "fast_greedy"
    edge_dir = clustering_dir / "edge_betweenness"
    infomap_dir = clustering_dir / "infomap"

    for d in (clustering_dir, greedy_dir, edge_dir, infomap_dir):
        d.mkdir(parents=True, exist_ok=True)

    return greedy_dir, edge_dir, infomap_dir


# ============================================================
# CARGA DE GRAFO
# ============================================================

def build_graph(filepath: Path) -> nx.Graph:
    G = nx.Graph()
    with filepath.open("r", encoding="utf-8") as f:
        f.readline()  # ignorar cabecera
        for line in f:
            a, b, s = line.strip().split(",")
            s = float(s)
            G.add_edge(a, b, sim=s, weight=s, dist=1.0 - s)
    return G


# ============================================================
# GUARDAR JSON
# ============================================================

def guardar_json(data: dict, folder: Path, filename: str):
    path = folder / filename
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


# ============================================================
# INFOMAP
# ============================================================

def infomap_partition(G: nx.Graph):
    im = Infomap("--two-level --silent --seed 42")

    node_to_id = {n: i for i, n in enumerate(G.nodes())}
    id_to_node = {i: n for n, i in node_to_id.items()}

    for u, v, data in G.edges(data=True):
        im.add_link(node_to_id[u], node_to_id[v], data.get("weight", 1.0))

    im.run()

    comunidades = {}
    for node_id, module_id in im.modules:
        comunidades.setdefault(module_id, set()).add(id_to_node[node_id])

    return list(comunidades.values()), im.codelength


# ============================================================
# GIRVAN–NEWMAN COMPLETO
# ============================================================

def girvan_newman_full(G: nx.Graph):
    import copy
    H = copy.deepcopy(G)

    modularity_trace = []
    partitions_trace = []

    while H.number_of_edges() > 0:
        communities = list(nx.connected_components(H))
        partitions_trace.append(communities)
        modularity_trace.append(nx.community.modularity(G, communities))

        betw = nx.edge_betweenness_centrality(H)
        edge = max(betw, key=betw.get)
        H.remove_edge(*edge)

    best_idx = max(range(len(modularity_trace)), key=lambda i: modularity_trace[i])
    return partitions_trace[best_idx], modularity_trace[best_idx], modularity_trace


# ============================================================
# PLOT (solo almacenamiento)
# ============================================================

def plot_graph(G, communities, title, folder: Path, filename: str):
    pos = nx.spring_layout(G, seed=123)

    color_map = {}
    cid = 0
    for com in communities:
        for n in com:
            color_map[n] = cid
        cid += 1

    colors = [color_map[n] for n in G.nodes()]

    plt.figure(figsize=(10, 8))
    nx.draw(
        G, pos,
        node_color=colors, cmap=plt.cm.tab20,
        node_size=350, with_labels=True,
        font_size=8, edge_color="black"
    )
    plt.title(title)
    plt.savefig(folder / filename, dpi=300, bbox_inches="tight")
    plt.close()


# ============================================================
# EJECUCIÓN DESDE PIPELINE
# ============================================================

def ejecutar_clustering(modo: str, score: int):
    """
    Ejecuta los 3 algoritmos sobre la red y devuelve:
        {
            "fast_greedy": n_clusters,
            "edge_betweenness": n_clusters,
            "infomap": n_clusters
        }
    """
    print(f"• Clustering (FG / EB / I)...", end="")

    base = RESULTADOS_DIR / "redes" / f"{modo}_score{score}"
    path_red = base / f"red_{modo}_score{score}.txt"

    greedy_dir, edge_dir, infomap_dir = preparar_rutas(modo, score)

    G = build_graph(path_red)

    resumen = {}

    # --------------------------------------------------------
    # 1) Greedy Modularity
    # --------------------------------------------------------
    communities = list(greedy_modularity_communities(G, weight="weight"))
    Q = modularity(G, communities)

    guardar_json(
        {
            "algorithm": "fast_greedy",
            "modularity": Q,
            "communities": [sorted(list(c)) for c in communities],
        },
        greedy_dir,
        f"fast_greedy_{modo}_score{score}.json",
    )
    # PNG
    plot_graph(G, communities, f"Algoritmo: Greedy modularity\nRed: {modo} | Score: {score}", greedy_dir, f"fast_greedy_{modo}_score{score}.png")

    resumen["fast_greedy"] = len(communities)

    # --------------------------------------------------------
    # 2) Edge betweenness
    # --------------------------------------------------------
    best_coms, best_Q, Q_list = girvan_newman_full(G)

    guardar_json(
        {
            "algorithm": "edge_betweenness",
            "best_modularity": best_Q,
            "communities": [sorted(list(c)) for c in best_coms],
            "modularity_trace": Q_list,
        },
        edge_dir,
        f"edge_betweenness_{modo}_score{score}.json",
    )
    # PNG
    plot_graph(G, best_coms, f"Algoritmo: Edge betweenness\nRed: {modo} | Score: {score}", edge_dir, f"edge_betweenness_{modo}_score{score}.png")

    resumen["edge_betweenness"] = len(best_coms)

    # --------------------------------------------------------
    # 3) Infomap
    # --------------------------------------------------------
    com_infomap, L = infomap_partition(G)

    guardar_json(
        {
            "algorithm": "infomap",
            "codelength": L,
            "communities": [sorted(list(c)) for c in com_infomap],
        },
        infomap_dir,
        f"infomap_{modo}_score{score}.json",
    )
    # PNG
    plot_graph(G, com_infomap, f"Algoritmo: Infomap\nRed: {modo} | Score: {score}", infomap_dir, f"infomap_{modo}_score{score}.png")

    resumen["infomap"] = len(com_infomap)

    print(" ✓ OK")
    return resumen