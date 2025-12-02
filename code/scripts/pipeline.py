"""
Módulo: pipeline.py

Descripción:
    Punto de entrada único del proyecto.

    Ejecuta de forma secuencial, para cada modo (hpo y manual) y cada score:
        1. Generación de la red STRING
        2. Análisis topológico preliminar
        3. Clustering (Greedy, Girvan–Newman, Infomap)
        4. Análisis funcional ORA por cada clúster
        5. Comparativa ORA entre GO, KEGG y Reactome por clúster

    Este es el ÚNICO archivo que debe ejecutarse directamente:

        python scripts/pipeline.py

    Todos los demás archivos en /scripts/ son módulos internos.
"""

from generar_red import generar_red
from analizar_topologia_red import analizar_topologia
from clustering import ejecutar_clustering
from analisis_funcional_clusters import analisis_funcional_clusters
from analisis_funcional_comparativo import analisis_funcional_comparativo
from paths import LISTA_GENES_MANUAL


# ============================================================
# CONFIGURACIÓN GENERAL
# ============================================================

HPO_TERM = "HP:0007354"
MODOS = ["hpo", "manual"]
SCORES = [300, 700, 900]


# ============================================================
# PIPELINE COMPLETO
# ============================================================

def pipeline():

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

            print("      - greedy_modularity:".ljust(28), f"{res_clust['greedy_modularity']} clusters")
            print("      - edge_betweenness:".ljust(28), f"{res_clust['edge_betweenness']} clusters")
            print("      - infomap:".ljust(28), f"{res_clust['infomap']} clusters")

            # =====================================================
            # 4) ORA POR CLUSTERS
            # =====================================================
            res_ora = analisis_funcional_clusters(modo, score)

            print("      - greedy_modularity:".ljust(28), f"{res_ora['greedy_modularity']} ORA OK")
            print("      - edge_betweenness:".ljust(28), f"{res_ora['edge_betweenness']} ORA OK")
            print("      - infomap:".ljust(28), f"{res_ora['infomap']} ORA OK")

            # =====================================================
            # 5) COMPARATIVA GO vs KEGG vs REACTOME
            # =====================================================
            analisis_funcional_comparativo(modo, score)


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    pipeline()