"""
Módulo: resumen_clustering.py

Descripción:
    Genera tablas resumen combinando:
        - número de clusters producidos por cada algoritmo
        - media de términos GO enriquecidos por cluster (solo ≥ 3 genes)

Entrada:
    result/redes/<modo>_score<score>/clustering/<algoritmo>/resultados.json
    result/redes/<modo>_score<score>/funcional/<algoritmo>/cluster_i/GO/enrichment_results.csv

Salida:
    results/resumen_clustering_<modo>.csv

Formato de cada celda:
    "<n_clusters> clusters | <media_GO> GO medio"
"""

from pathlib import Path
import json
import numpy as np
import pandas as pd

from paths import RESULTADOS_DIR, PROJECT_ROOT


# ------------------------------------------------------------
# Cargar comunidades desde clustering (JSON)
# ------------------------------------------------------------

def cargar_clusters(path_json: Path):
    if not path_json.exists():
        return None
    data = json.loads(path_json.read_text())
    clusters = data.get("communities", [])
    return clusters


# ------------------------------------------------------------
# Contar términos GO significativos para un cluster
# ------------------------------------------------------------

def contar_GO_cluster(cluster_dir: Path) -> int:
    """
    Cluster_dir = .../funcional/<algoritmo>/cluster_X

    Se analiza SOLO:
        cluster_dir / "GO" / "enrichment_results.csv"
    """
    go_csv = cluster_dir / "GO" / "enrichment_results.csv"
    if not go_csv.exists():
        return 0

    df = pd.read_csv(go_csv)

    if df.empty or "Adjusted P-value" not in df.columns:
        return 0

    # conteo de términos significativos
    df_sig = df[df["Adjusted P-value"] < 0.05]
    return len(df_sig)


# ------------------------------------------------------------
# Calcular media GO para todos los clusters de un algoritmo
# ------------------------------------------------------------

def media_GO_algoritmo(modo: str, score: int, algoritmo: str, clusters: list[list[str]]):
    base = RESULTADOS_DIR / "redes" / f"{modo}_score{score}" / "funcional" / algoritmo

    conteos = []

    for idx, comunidad in enumerate(clusters):
        if len(comunidad) < 3:
            continue  # ignorar clusters pequeños

        cluster_dir = base / f"cluster_{idx}"
        conteos.append(contar_GO_cluster(cluster_dir))

    if not conteos:
        return 0.0

    return float(np.mean(conteos))


# ------------------------------------------------------------
# TABLA PRINCIPAL
# ------------------------------------------------------------

def generar_tabla_clusters_avanzada(modo: str, resumen_clusters: dict):
    """
    resumen_clusters tiene la forma:
        {
            score: {
                "fast_greedy": <n_clusters>,
                "edge_betweenness": <n_clusters>,
                "infomap": <n_clusters>,
            },
            ...
        }
    Esta función añade media_GO y construye la tabla final.
    """

    algoritmos = ["infomap", "fast_greedy", "edge_betweenness"]

    filas = []

    for score, dicc in resumen_clusters.items():

        fila = {"Red": modo, "Score": score}

        for alg in algoritmos:
            # cargar clusters
            path_json = (
                RESULTADOS_DIR / "redes" / f"{modo}_score{score}"
                / "clustering" / alg / f"{alg}_{modo}_score{score}.json"
            )
            clusters = cargar_clusters(path_json)

            if clusters is None:
                fila[alg] = "0 clusters | 0 GO medio"
                continue

            n_clusters = len(clusters)
            media_go = media_GO_algoritmo(modo, score, alg, clusters)

            fila[alg] = f"{n_clusters} clusters | {round(media_go, 2)} GO medio"

        filas.append(fila)

    df = pd.DataFrame(filas)

    # ordenar por score
    df = df.sort_values(["Red", "Score"])

    # guardar
    out_path = RESULTADOS_DIR / f"resumen_clustering_{modo}.csv"
    df.to_csv(out_path, index=False)

    try:
        rel = out_path.relative_to(PROJECT_ROOT)
    except ValueError:
        rel = out_path

    print(f"    ✓ Tabla avanzada clustering ({modo}) guardada → {rel}")
    return df