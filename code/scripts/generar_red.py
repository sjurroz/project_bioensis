"""
Módulo: generar_red.py

Descripción:
    Genera una red STRING en modo HPO o en modo manual.

    Este módulo NO es ejecutable directamente. Debe ser invocado
    únicamente desde pipeline.py mediante la función:

        generar_red(modo, score, hpo=None, genes_file=None)

Entrada:
    - modo: 'hpo' o 'manual'
    - score: score mínimo requerido por STRING (0–1000)
    - hpo: ID de término HPO (solo modo 'hpo')
    - genes_file: archivo con lista manual de genes (solo modo 'manual')

Salida:
    results/redes/<modo>_score<score>/
        red_<modo>_score<score>.txt
        red_<modo>_score<score>.png
"""

import io
import json
from pathlib import Path

import requests
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

from paths import PROJECT_ROOT, RESULTADOS_DIR


# ============================================================
# CONSTANTES
# ============================================================

HPO_ANNOTATIONS_URL = (
    "http://purl.obolibrary.org/obo/hp/hpoa/phenotype_to_genes.txt"
)
SPECIES_ID = 9606


# ============================================================
# FUNCIONES AUXILIARES
# ============================================================

def obtener_genes_hpo(term_id: str) -> list[str]:
    response = requests.get(HPO_ANNOTATIONS_URL)
    response.raise_for_status()

    df = pd.read_csv(io.StringIO(response.text), sep="\t", comment="#")
    df = df[df["hpo_id"] == term_id]

    genes = sorted(df["gene_symbol"].unique().tolist())

    if not genes:
        raise ValueError(f"No se encontraron genes asociados a {term_id}")

    return genes


def cargar_lista_manual(path: Path) -> list[str]:
    if not path.exists():
        raise FileNotFoundError(f"No existe el archivo: {path}")

    if path.suffix.lower() == ".json":
        with open(path, "r") as f:
            genes = json.load(f)
    else:
        with open(path, "r") as f:
            genes = [line.strip() for line in f if line.strip()]

    genes = sorted(set(genes))

    if not genes:
        raise ValueError("La lista manual de genes está vacía.")

    return genes


def consultar_string(genes: list[str], score: int) -> pd.DataFrame:
    api_url = "https://string-db.org/api/tsv/network"

    payload = {
        "identifiers": "%0d".join(genes),
        "species": SPECIES_ID,
        "required_score": score,
        "network_flavor": "evidence",
    }

    response = requests.post(api_url, data=payload)
    response.raise_for_status()

    return pd.read_csv(io.StringIO(response.text), sep="\t")


def visualizar_red(df: pd.DataFrame, threshold: int, out_png: Path, titulo: str, n_nodos: int):
    G = nx.from_pandas_edgelist(df, "gen1", "gen2", edge_attr="score")

    plt.figure(figsize=(11, 11))
    pos = nx.spring_layout(G, seed=42, k=0.4)

    nx.draw_networkx_nodes(G, pos, node_size=500, node_color="lightblue", alpha=0.9)
    nx.draw_networkx_edges(
        G, pos,
        width=[2 + float(s) * 1.3 for s in df["score"]],
        alpha=0.5
    )
    nx.draw_networkx_labels(G, pos, font_size=8)

    plt.title(f"{titulo}\nScore mínimo: {threshold} | Nodos: {n_nodos}", fontsize=13)
    plt.axis("off")
    plt.tight_layout()
    plt.savefig(out_png, dpi=300)
    plt.close()


# ============================================================
# FUNCIÓN PRINCIPAL
# ============================================================

def generar_red(modo: str, score: int, hpo: str = None, genes_file: Path = None):
    """
    Genera y guarda la red STRING según el modo especificado.
    """

    print("• Generando red... ", end="", flush=True)

    out_dir = RESULTADOS_DIR / "redes" / f"{modo}_score{score}"
    out_dir.mkdir(parents=True, exist_ok=True)

    txt_out = out_dir / f"red_{modo}_score{score}.txt"
    png_out = out_dir / f"red_{modo}_score{score}.png"

    # --------------------------------------------------------
    # 1) Obtener genes
    # --------------------------------------------------------
    if modo == "hpo":
        genes = obtener_genes_hpo(hpo)
        titulo = f"Red STRING – Genes desde HPO ({hpo})"
    else:
        genes = cargar_lista_manual(Path(genes_file))
        titulo = "Red STRING – Lista manual de genes"

    # --------------------------------------------------------
    # 2) Llamada a STRING
    # --------------------------------------------------------
    df_raw = consultar_string(genes, score)

    df_clean = df_raw[["preferredName_A", "preferredName_B", "score"]].copy()
    df_clean.columns = ["gen1", "gen2", "score"]
    df_clean.to_csv(txt_out, index=False)

    # --------------------------------------------------------
    # 3) Visualización
    # --------------------------------------------------------
    n_nodos = len(set(df_clean["gen1"]).union(df_clean["gen2"]))
    visualizar_red(df_clean, score, png_out, titulo, n_nodos)

    print("✓ OK")