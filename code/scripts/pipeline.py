"""
Módulo: pipeline.py

Descripción:
    Punto de entrada único del proyecto.

    Ejecuta de forma secuencial, para cada modo (hpo y manual) y cada score:
        1. Generación de la red STRING
        2. Análisis topológico preliminar
        3. Clustering (Greedy, Girvan–Newman, Infomap)
        4. Análisis funcional ORA por cada clúster

    5. Generación de tablas comparativas para las distintas combinaciones exploradas
"""
import random

import numpy as np

from generar_red import generar_red
from analizar_topologia_red import analizar_topologia
from clustering import ejecutar_clustering
from analisis_funcional_clusters import analisis_funcional_clusters
from resumen_clustering import generar_tabla_clusters_avanzada
from paths import LISTA_GENES_MANUAL

# ============================================================
# CONFIGURACIÓN GENERAL
# ============================================================

HPO_TERM = "HP:0007354"
MODOS = ["hpo", "manual"]
SCORES = [300, 700, 900]

# Diccionarios para almacenar resultados
tabla_clusters = {
    "hpo": {300: {}, 700: {}, 900: {}},
    "manual": {300: {}, 700: {}, 900: {}},
}

# Semilla para garantizar reproducibilidad
SEED = 42
random.seed(SEED)
np.random.seed(SEED)

# ============================================================
# PIPELINE COMPLETO
# ============================================================

def pipeline():

    tabla_clusters = {
        "hpo": {300: {}, 700: {}, 900: {}},
        "manual": {300: {}, 700: {}, 900: {}},
    }

    for modo in MODOS:
        for score in SCORES:

            print("--------------------------------------------------")
            print(f" Procesando red: modo = {modo} | score = {score}")
            print("--------------------------------------------------")

            # =====================================================
            # 1) GENERAR RED STRING
            # =====================================================
            if modo == "hpo":
                generar_red(
                    modo="hpo",
                    score=score,
                    hpo=HPO_TERM
                )
            else:
                generar_red(
                    modo="manual",
                    score=score,
                    genes_file=LISTA_GENES_MANUAL
                )

            # =====================================================
            # 2) ANÁLISIS TOPOLOGÍA PRELIMINAR
            # =====================================================
            analizar_topologia(modo, score)

            # =====================================================
            # 3) CLUSTERING
            # =====================================================
            res_clust = ejecutar_clustering(modo, score)

            # Guardar número de clusters para la tabla comparativa
            tabla_clusters[modo][score] = res_clust

            print("      - fast_greedy:".ljust(28), f"{res_clust['fast_greedy']} clusters")
            print("      - edge_betweenness:".ljust(28), f"{res_clust['edge_betweenness']} clusters")
            print("      - infomap:".ljust(28), f"{res_clust['infomap']} clusters")

            # =====================================================
            # 4) ORA POR CLUSTERS
            # =====================================================
            res_ora = analisis_funcional_clusters(modo, score)

            print("      - fast_greedy:".ljust(28), f"{res_ora['fast_greedy']} ORA ✓ OK")
            print("      - edge_betweenness:".ljust(28), f"{res_ora['edge_betweenness']} ORA ✓ OK")
            print("      - infomap:".ljust(28), f"{res_ora['infomap']} ORA ✓ OK")

    # =====================================================
    # 5) TABLAS COMPARATIVAS
    # =====================================================

    print("\n-------------------------------------------------------------------------")
    print(" Generando tablas comparativas para las distinas configuraciones")
    print("\n-------------------------------------------------------------------------")

    generar_tabla_clusters_avanzada("hpo", tabla_clusters["hpo"])
    generar_tabla_clusters_avanzada("manual", tabla_clusters["manual"])


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    pipeline()