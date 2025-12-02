"""
Módulo: pipeline.py

Descripción:
    Punto de entrada único del proyecto.

    Ejecuta de forma secuencial:
        1. Generación de redes STRING (HPO y manual)
        2. Análisis topológico preliminar
        3. Clustering (Greedy, Girvan–Newman, Infomap)

    Este es el ÚNICO archivo que debe ejecutarse:

        python pipeline.py

    Todos los demás archivos en /scripts/ son módulos internos.
"""

from pathlib import Path

# Importar módulos del proyecto
from scripts.generar_red import generar_red
from scripts.analizar_topologia_red import analizar_topologia
from scripts.clustering import ejecutar_clustering


# ============================================================
# CONFIGURACIÓN DEL PIPELINE
# ============================================================

HPO_TERM = "HP:0007354"

BASE = Path(__file__).resolve().parents[0].parent   # raíz del proyecto
GENES_MANUAL = BASE / "genes" / "lista_genes_manual.json"

MODOS = ["hpo", "manual"]
SCORES = [300, 700, 900]


# ============================================================
# EJECUCIÓN DEL PIPELINE
# ============================================================

def pipeline():
    print("\n===== INICIANDO PIPELINE COMPLETO =====\n")

    for modo in MODOS:
        for score in SCORES:

            print("--------------------------------------------------")
            print(f"Procesando: modo={modo} | score={score}")
            print("--------------------------------------------------")

            # ==========================================
            # 1) GENERAR RED
            # ==========================================
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
                    genes_file=str(GENES_MANUAL)
                )

            # ==========================================
            # 2) TOPOLOGÍA PRELIMINAR
            # ==========================================
            analizar_topologia(modo, score)

            # ==========================================
            # 3) CLUSTERING
            # ==========================================
            ejecutar_clustering(modo, score)

    print("\n✓ Pipeline completado correctamente.\n")


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    pipeline()