"""
Script: comparar_redes_genes.py

Descripción:
    Compara dos redes de interacción génica (manual y HPO) generadas
    a partir de la API de STRING. Evalúa la similitud entre sus aristas
    y calcula métricas estructurales relevantes: número de nodos,
    aristas, grado medio, densidad, componentes conexas y coincidencia
    de interacciones entre ambas redes. Los resultados se guardan en
    archivos CSV y JSON para su análisis posterior.
"""

import pandas as pd
import networkx as nx
import json
from pathlib import Path

# === Parámetros globales ===
INPUT_NETWORK_MANUAL = "network_string_manual.txt"
INPUT_NETWORK_HPO = "network_string_hpo.txt"
OUTPUT_COMPARISON_FILE = "comparacion_redes_genes.csv"
OUTPUT_DETAILS_FILE = "detalles_comparacion_redes.json"

# === 1. Funciones auxiliares ===
def cargar_red(ruta: str) -> nx.Graph:
    """Carga una red génica desde un archivo CSV/TXT con columnas gen1, gen2, score."""
    if not Path(ruta).exists():
        raise FileNotFoundError(f"No se encontró el archivo: {ruta}")
    df = pd.read_csv(ruta)
    return nx.from_pandas_edgelist(df, "gen1", "gen2", edge_attr="score")

def obtener_metricas_red(G: nx.Graph) -> dict:
    """Calcula métricas estructurales relevantes para una red de genes."""
    if len(G) == 0:
        return {"n_nodos": 0, "n_aristas": 0, "grado_medio": 0, "densidad": 0, "n_componentes": 0}
    return {
        "n_nodos": G.number_of_nodes(),
        "n_aristas": G.number_of_edges(),
        "grado_medio": round(sum(dict(G.degree()).values()) / G.number_of_nodes(), 2),
        "densidad": round(nx.density(G), 4),
        "n_componentes": nx.number_connected_components(G),
    }

# === 2. Cargar redes ===
print("🔹 Cargando redes...")
red_manual = cargar_red(INPUT_NETWORK_MANUAL)
red_hpo = cargar_red(INPUT_NETWORK_HPO)

# === 3. Calcular métricas individuales ===
metricas_manual = obtener_metricas_red(red_manual)
metricas_hpo = obtener_metricas_red(red_hpo)

# === 4. Comparar aristas ===
edges_manual = {frozenset(e) for e in red_manual.edges()}
edges_hpo = {frozenset(e) for e in red_hpo.edges()}

aristas_comunes = edges_manual & edges_hpo
solo_manual = edges_manual - edges_hpo
solo_hpo = edges_hpo - edges_manual

porcentaje_solapamiento = round((len(aristas_comunes) / len(edges_manual | edges_hpo)) * 100, 2)

# === 5. Resumen comparativo ===
print("🔍 Comparación de redes de interacción")
print(f"--------------------------------------")
print(f"Aristas en red manual: {len(edges_manual)}")
print(f"Aristas en red HPO:    {len(edges_hpo)}")
print(f"Aristas en ambas:      {len(aristas_comunes)}")
print(f"Solo en manual:        {len(solo_manual)}")
print(f"Solo en HPO:           {len(solo_hpo)}")
print(f"Solapamiento relativo: {porcentaje_solapamiento}%\n")

# === 6. Consolidar métricas globales ===
df_comparacion = pd.DataFrame([
    {"red": "manual", **metricas_manual},
    {"red": "hpo", **metricas_hpo},
    {"red": "comparacion", "n_nodos": len(red_manual.nodes() | red_hpo.nodes()),
     "n_aristas": len(edges_manual | edges_hpo), "grado_medio": None,
     "densidad": None, "n_componentes": None}
])

df_comparacion.to_csv(OUTPUT_COMPARISON_FILE, index=False)
print(f"✅ Resumen guardado en {OUTPUT_COMPARISON_FILE}")

# === 7. Guardar detalles adicionales ===
detalles = {
    "interseccion_aristas": sorted([list(e) for e in aristas_comunes]),
    "solo_manual": sorted([list(e) for e in solo_manual]),
    "solo_hpo": sorted([list(e) for e in solo_hpo]),
    "porcentaje_solapamiento": porcentaje_solapamiento,
    "metricas_manual": metricas_manual,
    "metricas_hpo": metricas_hpo,
}

with open(OUTPUT_DETAILS_FILE, "w") as f:
    json.dump(detalles, f, indent=4)
print(f"✅ Detalles guardados en {OUTPUT_DETAILS_FILE}")