import networkx as nx
import matplotlib.pyplot as plt
from networkx.algorithms.community.quality import modularity
import os
import json
from networkx.algorithms.community import greedy_modularity_communities
from infomap import Infomap


# =============================================================
# FUNCIONES DE PREPARACIÓN DE RUTAS
# =============================================================

def preparar_rutas(nombre):
    """
    Crea:
      results/redes/<nombre_sin_extension>/clustering/
            ├── greedy_modularity/
            ├── edge_betweenness/
            └── infomap/
    Devuelve las 3 rutas.
    """
    base_name = nombre.replace(".txt", "")

    base_dir = os.path.join("results", "redes", base_name)
    clustering_dir = os.path.join(base_dir, "clustering")

    greedy_dir = os.path.join(clustering_dir, "greedy_modularity")
    edge_dir = os.path.join(clustering_dir, "edge_betweenness")
    infomap_dir = os.path.join(clustering_dir, "infomap")

    for d in [base_dir, clustering_dir, greedy_dir, edge_dir, infomap_dir]:
        os.makedirs(d, exist_ok=True)

    return greedy_dir, edge_dir, infomap_dir



# =============================================================
# FUNCIONES GENERALES
# =============================================================

def build_graph_from_file(filepath):
    """Lee archivo gen1,gen2,score y crea grafo NetworkX."""
    G = nx.Graph()

    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                a, b, s = line.split(",")
                s = float(s)
                G.add_edge(a, b, sim=s, weight=s, dist=1.0 - s)
            except:
                print("Línea inválida (se ignora):", line)

    return G


def guardar_json(data, folder, filename):
    path = os.path.join(folder, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print(f"[OK] JSON guardado en: {path}")


# =============================================================
# PARTICIÓN INFOMAP
# =============================================================

def infomap_partition(G):
    im = Infomap("--two-level --silent")

    node_to_id = {n: i for i, n in enumerate(G.nodes())}
    id_to_node = {i: n for n, i in node_to_id.items()}

    for u, v, data in G.edges(data=True):
        w = data.get("weight", 1.0)
        im.add_link(node_to_id[u], node_to_id[v], w)

    im.run()

    communities_dict = {}
    for node_id, module_id in im.modules:
        node = id_to_node[node_id]
        if module_id not in communities_dict:
            communities_dict[module_id] = set()
        communities_dict[module_id].add(node)

    communities = list(communities_dict.values())
    return communities, im.codelength



# =============================================================
# GIRVAN–NEWMAN COMPLETO (PICO GLOBAL)
# =============================================================

def girvan_newman_full(G):
    import copy
    H = copy.deepcopy(G)

    modularity_trace = []
    partitions_trace = []

    while H.number_of_edges() > 0:
        communities = list(nx.connected_components(H))
        partitions_trace.append(communities)

        Q = nx.community.modularity(G, communities)
        modularity_trace.append(Q)

        betw = nx.edge_betweenness_centrality(H)
        edge = max(betw, key=betw.get)
        H.remove_edge(*edge)

    best_index = max(range(len(modularity_trace)), key=lambda i: modularity_trace[i])

    best_mod = modularity_trace[best_index]
    best_coms = partitions_trace[best_index]

    return best_coms, best_mod, modularity_trace



# =============================================================
# GRAFICADO
# =============================================================

def plot_graph(G, communities, title, folder, filename, extra_text=""):
    os.makedirs(folder, exist_ok=True)
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
        node_color=colors,
        cmap=plt.cm.tab20,
        node_size=350,
        with_labels=True,
        font_size=8,
        edge_color="black"
    )
    plt.title(title)

    if extra_text:
        plt.text(0.5, 1.03, extra_text, transform=plt.gca().transAxes,
                 ha="center", fontsize=12, color="darkred", fontweight="bold")

    path = os.path.join(folder, filename)
    plt.savefig(path, dpi=300, bbox_inches="tight")
    plt.close()


def plot_modularity_trace(Q_list, folder, filename):
    os.makedirs(folder, exist_ok=True)

    plt.figure(figsize=(8, 5))
    plt.plot(Q_list, marker="o")
    plt.title("Evolución de la modularidad (Girvan–Newman)")
    plt.xlabel("Iteración")
    plt.ylabel("Modularidad Q")
    plt.grid(True)

    path = os.path.join(folder, filename)
    plt.savefig(path, dpi=300, bbox_inches="tight")
    plt.close()



# =============================================================
# CONDUCTANCIA
# =============================================================

def conductance(G, community):
    C = set(community)
    notC = set(G.nodes()) - C

    cut_edges = sum(1 for u, v in G.edges() if (u in C) != (v in C))
    volC = sum(dict(G.degree(C)).values())
    volN = sum(dict(G.degree(notC)).values())

    if min(volC, volN) == 0:
        return 0.0

    return cut_edges / min(volC, volN)


def conductance_report(G, communities):
    values = [conductance(G, c) for c in communities]
    return {
        "per_community": values,
        "mean": sum(values) / len(values),
        "min": min(values),
        "max": max(values)
    }



# =============================================================
# EJECUCIÓN DE ALGORITMOS
# =============================================================

def ejecutar_algoritmo_greedy_modularity(G, ruta):
    communities = list(greedy_modularity_communities(G, weight="weight"))
    Q = modularity(G, communities, weight="weight")
    cond = conductance_report(G, communities)

    plot_graph(G, communities, "Comunidades Greedy Modularity",
               ruta, "greedy_modularity.png")

    data = {
        "algorithm": "greedy_modularity",
        "modularity": Q,
        "num_communities": len(communities),
        "communities": [sorted(list(c)) for c in communities],
        "conductance": cond,
        "graph": {"nodes": G.number_of_nodes(), "edges": G.number_of_edges()}
    }

    guardar_json(data, ruta, "resultados_greedy_modularity.json")


def ejecutar_algoritmo_edge_betweenness(G, ruta):
    best_coms, best_Q, Q_trace = girvan_newman_full(G)
    cond = conductance_report(G, best_coms)

    plot_graph(
        G, best_coms,
        "Mejor partición GN (Edge Betweenness)",
        ruta, "gn_best.png",
        extra_text=f"Modularidad = {best_Q:.4f}"
    )

    plot_modularity_trace(Q_trace, ruta, "gn_trace.png")

    data = {
        "algorithm": "edge_betweenness_girvan_newman",
        "best_modularity": best_Q,
        "num_communities": len(best_coms),
        "best_partition": [sorted(list(c)) for c in best_coms],
        "conductance": cond,
        "modularity_trace": Q_trace,
        "graph": {"nodes": G.number_of_nodes(), "edges": G.number_of_edges()}
    }

    guardar_json(data, ruta, "resultados_edge_betweenness.json")


def ejecutar_algoritmo_infomap(G, ruta):
    communities, L = infomap_partition(G)
    cond = conductance_report(G, communities)

    plot_graph(
        G, communities,
        f"Comunidades Infomap (L={L:.4f})",
        ruta, "infomap_comunidades.png"
    )

    data = {
        "algorithm": "infomap",
        "codelength": L,
        "num_communities": len(communities),
        "communities": [sorted(list(c)) for c in communities],
        "conductance": cond,
        "graph": {"nodes": G.number_of_nodes(), "edges": G.number_of_edges()}
    }

    guardar_json(data, ruta, "resultados_infomap.json")



# =============================================================
# MAIN
# =============================================================

def main():
    ruta = "redes/redes/hpo_score900/red_hpo_score900.txt"
    nombre = "red_hpo_score900.txt"

    print(f"LEYENDO GRAFO DESDE {ruta}")
    G = build_graph_from_file(ruta)
    print(f"Grafo cargado: {G.number_of_nodes()} nodos, {G.number_of_edges()} aristas.\n")

    global greedy_dir, edge_dir, infomap_dir
    greedy_dir, edge_dir, infomap_dir = preparar_rutas(nombre)

    ejecutar_algoritmo_greedy_modularity(G, greedy_dir)
    ejecutar_algoritmo_edge_betweenness(G, edge_dir)
    ejecutar_algoritmo_infomap(G, infomap_dir)


if __name__ == "__main__":
    main()
