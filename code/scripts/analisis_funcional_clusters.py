"""
Módulo: analisis_funcional_clusters.py

Descripción:
    Ejecuta ORA (GO / KEGG / Reactome) para cada clúster de cada algoritmo
    (Greedy, GN, Infomap), únicamente para clusters con ≥ 5 genes.

Salida:
    results/redes/<modo>_score<score>/funcional/<algoritmo>/cluster_<i>/
        GO/enrichment_results.csv
        KEGG/enrichment_results.csv
        Reactome/enrichment_results.csv
"""

from pathlib import Path
import json
import numpy as np
import matplotlib.pyplot as plt
import gseapy as gp

from paths import RESULTADOS_DIR


# ============================================================
# UTILIDADES
# ============================================================

def limpiar_texto(txt: str, max_palabras=4) -> str:
    txt = txt.split("(")[0].strip()
    palabras = txt.split()
    return " ".join(palabras[:max_palabras])


def graficar_top(df, out_png, n=10):
    df = df.sort_values("Adjusted P-value").head(n).iloc[::-1].copy()
    df["Term_clean"] = df["Term"].apply(limpiar_texto)

    plt.figure(figsize=(11, 0.55 * len(df)))
    plt.barh(df["Term_clean"], -np.log10(df["Adjusted P-value"]), color="#1976D2")
    plt.xlabel("-log10(Adjusted P-value)")
    plt.title("ORA – Categorías representadas")
    plt.tight_layout()
    plt.savefig(out_png, dpi=300)
    plt.close()


# ============================================================
# ORA INDIVIDUAL PARA UNA BASE
# ============================================================

def ora_base(genes: list[str], base: str, out_dir: Path):
    out_dir.mkdir(parents=True, exist_ok=True)

    enr = gp.enrichr(
        gene_list=genes,
        gene_sets=[base],
        organism="Human",
        cutoff=0.05
    )

    df = enr.results
    if df is None or df.empty:
        (out_dir / "enrichment_results.csv").write_text("NO RESULTS")
        return

    df.to_csv(out_dir / "enrichment_results.csv", index=False)
    graficar_top(df, out_dir / "enrichment_plot.png")


# ============================================================
# ORA POR CLUSTER
# ============================================================

def analisis_funcional_clusters(modo: str, score: int):
    """
    Ejecuta ORA para cada cluster de cada algoritmo.
    Devuelve un diccionario:
        { algoritmo: n_ORAs_ejecutados }
    """
    print(f"• ORA por clusters...", end="")

    base_red = RESULTADOS_DIR / "redes" / f"{modo}_score{score}"
    clustering_dir = base_red / "clustering"
    out_base = base_red / "funcional"
    out_base.mkdir(parents=True, exist_ok=True)

    algoritmos = {
        "fast_greedy": clustering_dir / "fast_greedy" / f"fast_greedy_{modo}_score{score}.json",
        "edge_betweenness": clustering_dir / "edge_betweenness" / f"edge_betweenness_{modo}_score{score}.json",
        "infomap": clustering_dir / "infomap" / f"infomap_{modo}_score{score}.json",
    }

    resumen_oras = {}

    for algoritmo, json_path in algoritmos.items():
        if not json_path.exists():
            resumen_oras[algoritmo] = 0
            continue

        data = json.loads(json_path.read_text())
        clusters = data.get("communities", [])

        out_alg = out_base / algoritmo
        out_alg.mkdir(parents=True, exist_ok=True)

        n_ora = 0
        for idx, cluster in enumerate(clusters):
            if len(cluster) < 3:
                continue

            genes = [g.upper() for g in cluster]
            cdir = out_alg / f"cluster_{idx}"
            cdir.mkdir(parents=True, exist_ok=True)

            ora_base(genes, "GO_Biological_Process_2023", cdir / "GO")
            ora_base(genes, "KEGG_2021_Human", cdir / "KEGG")
            ora_base(genes, "Reactome_2022", cdir / "Reactome")

            n_ora += 1

        resumen_oras[algoritmo] = n_ora

    print(" ✓ OK")
    return resumen_oras