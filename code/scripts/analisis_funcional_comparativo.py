"""
Módulo: analisis_funcional_comparativo.py

Descripción:
    Compara los resultados de ORA por cluster entre las bases de datos
    GO, KEGG y Reactome. Para cada cluster, genera:

        - tabla comparativa (csv)
        - índice de convergencia funcional (txt)
        - heatmap de –log10(padj)

Entrada:
    results/redes/<modo>_score<score>/funcional/<algoritmo>/cluster_i/<DB>/enrichment_results.csv

Salida:
    results/redes/<modo>_score<score>/funcional_comparativo/<algoritmo>_cluster_i/
        comparativa.csv
        convergencia.txt
        heatmap.png
"""

from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from paths import PROJECT_ROOT, RESULTADOS_DIR


# ======================================================================
# Cargar un ORA individual (GO / KEGG / Reactome)
# ======================================================================

def cargar_resultados_db(cluster_dir: Path, db: str):
    """
    Carga enrichment_results.csv dentro de:
        cluster_x/GO/
        cluster_x/KEGG/
        cluster_x/Reactome/
    """
    csv_path = cluster_dir / db / "enrichment_results.csv"
    if not csv_path.exists():
        return None

    df = pd.read_csv(csv_path)
    if df.empty:
        return None

    return df


# ======================================================================
# Tabla comparativa
# ======================================================================

def crear_tabla_comparativa(df_go, df_kegg, df_reactome):
    """
    Construye tabla:

                top_term | padj | minuslog10_padj
    GO
    KEGG
    Reactome
    """
    datos = {}

    bases = {
        "GO": df_go,
        "KEGG": df_kegg,
        "Reactome": df_reactome
    }

    for base, df in bases.items():
        if df is None or df.empty:
            datos[base] = {
                "top_term": None,
                "padj": None,
                "minuslog10_padj": None
            }
        else:
            d = df.sort_values("Adjusted P-value").iloc[0]
            padj = float(d["Adjusted P-value"])
            datos[base] = {
                "top_term": d["Term"],
                "padj": padj,
                "minuslog10_padj": -np.log10(padj) if padj > 0 else None
            }

    return pd.DataFrame.from_dict(datos, orient="index")


# ======================================================================
# Convergencia funcional
# ======================================================================

def calcular_convergencia(tabla: pd.DataFrame) -> int:
    """
    Convergencia = número de bases con algún término significativo.
    """
    return tabla["top_term"].notna().sum()


# ======================================================================
# Heatmap
# ======================================================================

def plot_heatmap(tabla: pd.DataFrame, out_png: Path):
    data = tabla[["minuslog10_padj"]]

    plt.figure(figsize=(4, 2.6))
    sns.heatmap(
        data,
        annot=True,
        cmap="Blues",
        vmin=0,
        linewidths=.5,
        cbar=False
    )
    plt.title("ORA – Convergencia funcional", fontsize=10)
    plt.tight_layout()
    plt.savefig(out_png, dpi=300)
    plt.close()


# ======================================================================
# FUNCIÓN PRINCIPAL
# ======================================================================

def analisis_funcional_comparativo(modo: str, score: int):
    """
    Ejecuta la comparativa funcional para todos los clusters
    de todos los algoritmos (solo clusters con ORA previo).
    """

    print("• Comparativa ORA (GO / KEGG / Reactome)... ", end="", flush=True)

    base_dir = RESULTADOS_DIR / "redes" / f"{modo}_score{score}"
    funcional_dir = base_dir / "funcional"
    out_dir = base_dir / "funcional_comparativo"
    out_dir.mkdir(parents=True, exist_ok=True)

    if not funcional_dir.exists():
        print("⚠️ sin resultados previos")
        return

    algoritmos = ["greedy_modularity", "edge_betweenness", "infomap"]

    for alg in algoritmos:
        alg_dir = funcional_dir / alg
        if not alg_dir.exists():
            continue

        for cluster_dir in sorted(alg_dir.glob("cluster_*")):

            # Cargar ORAs individuales
            df_go = cargar_resultados_db(cluster_dir, "GO")
            df_kegg = cargar_resultados_db(cluster_dir, "KEGG")
            df_reactome = cargar_resultados_db(cluster_dir, "Reactome")

            if df_go is None and df_kegg is None and df_reactome is None:
                continue  # no hay ORA real

            tabla = crear_tabla_comparativa(df_go, df_kegg, df_reactome)
            conv = calcular_convergencia(tabla)

            # Directorio de salida del cluster
            salida_cluster = out_dir / f"{alg}_{cluster_dir.name}"
            salida_cluster.mkdir(parents=True, exist_ok=True)

            # Guardar tabla
            tabla.to_csv(salida_cluster / "comparativa.csv")

            # Convergencia
            (salida_cluster / "convergencia.txt").write_text(str(conv))

            # Heatmap
            plot_heatmap(tabla, salida_cluster / "heatmap.png")

    print("✓ OK")