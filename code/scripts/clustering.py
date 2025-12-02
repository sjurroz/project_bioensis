"""
Módulo: clustering.py

Descripción:
    Ejecuta los 3 algoritmos de clustering (Greedy Modularity, Girvan–Newman
    e Infomap) sobre una red STRING previamente generada con generar_red.py.
    Produce gráficos y archivos JSON con los resultados de cada método.

Entrada:
    resultados/redes/<modo>_score<score>/red_<modo>_score<score>.txt

Salida:
    resultados/redes/<modo>_score<score>/clustering/
        ├── greedy_modularity/
        │       ├── greedy.png
        │       └── resultados.json
        ├── edge_betweenness/
        │       ├── gn.png
        │       └── resultados.json
        └── infomap/
                ├── infomap.png
                └── resultados.json

Contenido de cada JSON:
    {
        "algorithm": str,
        "modularity" | "best_modularity" | "codelength": float,
        "communities": list[list[str]],
        "modularity_trace": list[float] (solo Girvan–Newman)
    }

Propósito:
    Este módulo no es standalone. Debe ser invocado desde pipeline.py
    mediante la función pública:

        ejecutar_clustering(modo, score)

    Los resultados generados sirven para análisis comparativos entre
    métodos de clustering y para caracterizar la estructura modular
    de cada red antes de análisis funcionales posteriores.
"""

import json
from pathlib import Path
import networkx as nx
import matplotlib.pyplot as plt
from infomap import Infomap
from networkx.algorithms.community import greedy_modularity_communities
from networkx.algorithms.community.quality import modularity

BASE = Path(__file__).resolve().parents[2] # raíz del proyecto

# ============================================================
# PATHS
# ============================================================

def preparar_rutas(modo: str, score: int):
    """
    Crea estructura:

        resultados/redes/<modo>_score<score>/clustering/
                ├── greedy_modularity/
                ├── edge_betweenness/
                └── infomap/

    Devuelve: (ruta_greedy, ruta_edge, ruta_infomap)
    """

    BASE = Path(__file__).resolve().parents[2]      # raíz del proyecto
    base_dir = BASE / "resultados" / "redes" / f"{modo}_score{score}"
    clustering_dir = base_dir / "clustering"

    greedy_dir = clustering_dir / "greedy_modularity"
    edge_dir = clustering_dir / "edge_betweenness"
    infomap_dir = clustering_dir / "infomap"

    for d in [clustering_dir, greedy_dir, edge_dir, infomap_dir]:
        d.mkdir(parents=True, exist_ok=True)

    return greedy_dir, edge_dir, infomap_dir


# ============================================================
# CARGA DE GRAFO
# ============================================================

def build_graph(filepath: Path) -> nx.Graph:
    """Lee archivo gen1,gen2,score y crea un grafo NetworkX."""
    G = nx.Graph()

    with filepath.open("r", encoding="utf-8") as f:
        header = f.readline()  # ignorar cabecera
        for line in f:
            a, b, s = line.strip().split(",")
            s = float(s)
            G.add_edge(a, b, sim=s, weight=s, dist=1.0 - s)

    return G


# ============================================================
# UTILIDADES
# ============================================================

def guardar_json(data, folder: Path, filename: str):
    path = folder / filename
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    # Ruta relativa para el log
    try:
        rel = path.relative_to(BASE)
    except ValueError:
        rel = path  # fallback en caso improbable

    print(f"    [OK] JSON guardado en: {rel}")


# ============================================================
# INFOMAP
# ============================================================

def infomap_partition(G: nx.Graph):
    im = Infomap("--two-level --silent")

    node_to_id = {n: i for i, n in enumerate(G.nodes())}
    id_to_node = {i: n for n, i in node_to_id.items()}

    for u, v, data in G.edges(data=True):
        im.add_link(node_to_id[u], node_to_id[v], data.get("weight", 1.0))

    im.run()

    comunidades = {}
    for node_id, module_id in im.modules:
        node = id_to_node[node_id]
        comunidades.setdefault(module_id, set()).add(node)

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

    best_index = max(range(len(modularity_trace)), key=lambda i: modularity_trace[i])

    return partitions_trace[best_index], modularity_trace[best_index], modularity_trace


# ============================================================
# PLOTEADO
# ============================================================

def plot_graph(G, communities, title, folder, filename, extra_text=""):
    pos = nx.spring_layout(G, seed=123)

    # mapa de colores
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

    if extra_text:
        plt.text(
            0.5, 1.03, extra_text,
            transform=plt.gca().transAxes,
            ha="center", fontsize=12,
            color="darkred", fontweight="bold"
        )

    out_path = folder / filename
    plt.savefig(out_path, dpi=300, bbox_inches="tight")

# ============================================================
# EJECUCIÓN PÚBLICA DESDE EL PIPELINE
# ============================================================

def ejecutar_clustering(modo: str, score: int):
    """
    Ejecuta los 3 algoritmos de clustering sobre la red:

        resultados/redes/<modo>_score<score>/red_<modo>_score<score>.txt
    """

    print(f"\n▶ Ejecutando clustering para {modo}_score{score}")

    BASE = Path(__file__).resolve().parents[2]
    base_dir = BASE / "resultados" / "redes" / f"{modo}_score{score}"
    path_red = base_dir / f"red_{modo}_score{score}.txt"

    greedy_dir, edge_dir, infomap_dir = preparar_rutas(modo, score)

    # ----------------------------------------------------
    # CARGAR GRAFO
    # ----------------------------------------------------
    G = build_graph(path_red)
    print(f"    Grafo cargado: {G.number_of_nodes()} nodos | {G.number_of_edges()} aristas")

    # ----------------------------------------------------
    # 1) Greedy Modularity
    # ----------------------------------------------------
    print("    [1/3] Greedy Modularity...")
    communities = list(greedy_modularity_communities(G, weight="weight"))
    Q = modularity(G, communities)
    plot_graph(G, communities, "Greedy Modularity", greedy_dir, "greedy.png")
    guardar_json(
        {
            "algorithm": "greedy_modularity",
            "modularity": Q,
            "communities": [sorted(c) for c in communities],
        },
        greedy_dir, "resultados.json"
    )

    # ----------------------------------------------------
    # 2) Girvan–Newman
    # ----------------------------------------------------
    print("    [2/3] Edge Betweenness (Girvan–Newman)...")
    best_coms, best_Q, Q_list = girvan_newman_full(G)
    plot_graph(
        G, best_coms, "Girvan–Newman", edge_dir, "gn.png",
        extra_text=f"Q={best_Q:.4f}"
    )
    guardar_json(
        {
            "algorithm": "girvan_newman",
            "best_modularity": best_Q,
            "communities": [sorted(c) for c in best_coms],
            "modularity_trace": Q_list,
        },
        edge_dir, "resultados.json"
    )

    # ----------------------------------------------------
    # 3) Infomap
    # ----------------------------------------------------
    print("    [3/3] Infomap...")
    com_infomap, L = infomap_partition(G)
    plot_graph(G, com_infomap, f"Infomap (L={L:.4f})", infomap_dir, "infomap.png")
    guardar_json(
        {
            "algorithm": "infomap",
            "codelength": L,
            "communities": [sorted(c) for c in com_infomap],
        },
        infomap_dir, "resultados.json"
    )

    print(f"✓ Clustering completado para {modo}_score{score}\n")