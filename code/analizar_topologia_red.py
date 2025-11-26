"""
Módulo: analizar_topologia_red.py

Descripción:
    Análisis topológico preliminar y sencillo de una red STRING generada
    con generar_red.py. Calcula únicamente métricas globales esenciales y
    produce un único archivo JSON con resultados.

Entrada:
    resultados/redes/<modo>_score<score>/red_<modo>_score<score>.txt

Salida:
    resultados/redes/<modo>_score<score>/topologia/metricas_topologicas.json

Contenido del JSON:
    {
        "n_nodos": int,
        "n_aristas": int,
        "grado_medio": float,
        "densidad": float,
        "n_componentes": int,
        "coef_agrupamiento_medio": float,
        "diametro_gc": int | None,
        "longitud_camino_media_gc": float | None,
        "n_comunidades": int,
        "tamano_medio_comunidad": float,
        "modularidad_preliminar": float | None
    }

Estas métricas sirven como diagnóstico rápido antes de clustering avanzado.
"""

import json
from pathlib import Path

import networkx as nx
import pandas as pd


# ============================================================
# CARGA DE RED
# ============================================================

def _cargar_red(path_red: Path) -> nx.Graph:
    df = pd.read_csv(path_red)
    if df.empty:
        return nx.Graph()
    return nx.from_pandas_edgelist(df, "gen1", "gen2", edge_attr="score")


# ============================================================
# MÉTRICAS GLOBALES
# ============================================================

def _calcular_metricas_globales(G: nx.Graph) -> dict:
    n_nodos = G.number_of_nodes()
    n_aristas = G.number_of_edges()

    if n_nodos == 0:
        return {
            "n_nodos": 0,
            "n_aristas": 0,
            "grado_medio": 0.0,
            "densidad": 0.0,
            "n_componentes": 0,
            "coef_agrupamiento_medio": 0.0,
            "diametro_gc": None,
            "longitud_camino_media_gc": None,
            "n_comunidades": 0,
            "tamano_medio_comunidad": 0.0,
            "modularidad_preliminar": None
        }

    grados = dict(G.degree())
    grado_medio = round(sum(grados.values()) / n_nodos, 3)
    densidad = round(nx.density(G), 4)
    n_componentes = nx.number_connected_components(G)
    clustering_medio = round(nx.average_clustering(G), 4)

    # componente gigante
    componentes = list(nx.connected_components(G))
    largest = max(componentes, key=len)
    GC = G.subgraph(largest).copy()

    if GC.number_of_nodes() > 1:
        diametro = nx.diameter(GC)
        camino_medio = round(nx.average_shortest_path_length(GC), 3)
    else:
        diametro = 0
        camino_medio = 0.0

    # comunidades preliminares
    try:
        from networkx.algorithms.community import louvain_communities
        from networkx.algorithms.community.quality import modularity

        comunidades = louvain_communities(G, seed=42)
        modularidad_preliminar = modularity(G, comunidades) if n_aristas > 0 else None
    except ImportError:
        comunidades = [list(c) for c in componentes]
        modularidad_preliminar = None

    tam_medio_com = round(sum(len(c) for c in comunidades) / len(comunidades), 2)

    return {
        "n_nodos": n_nodos,
        "n_aristas": n_aristas,
        "grado_medio": grado_medio,
        "densidad": densidad,
        "n_componentes": n_componentes,
        "coef_agrupamiento_medio": clustering_medio,
        "diametro_gc": diametro,
        "longitud_camino_media_gc": camino_medio,
        "n_comunidades": len(comunidades),
        "tamano_medio_comunidad": tam_medio_com,
        "modularidad_preliminar": modularidad_preliminar,
    }


# ============================================================
# FUNCIÓN PÚBLICA
# ============================================================

def analizar_topologia(modo: str, score: int):
    """
    Análisis topológico preliminar de una red generada previamente por
    generar_red.py. Guarda las métricas en un archivo JSON.

    Este módulo debe ser invocado únicamente desde pipeline.py
    mediante:

        analizar_topologia(modo, score)
    """

    BASE = Path(__file__).resolve().parents[2]

    path_red = BASE / "resultados" / "redes" / f"{modo}_score{score}" / f"red_{modo}_score{score}.txt"
    out_dir = BASE / "resultados" / "redes" / f"{modo}_score{score}" / "topologia"
    out_dir.mkdir(parents=True, exist_ok=True)

    salida_json = out_dir / "metricas_topologicas.json"

    print(f"▶ Analizando topología: {modo}_score{score}")

    G = _cargar_red(path_red)
    metricas = _calcular_metricas_globales(G)

    with open(salida_json, "w") as f:
        json.dump(metricas, f, indent=4)

    try:
        rel = salida_json.relative_to(BASE)
    except ValueError:
        rel = salida_json

    print(f"    [OK] guardado en: {rel}")