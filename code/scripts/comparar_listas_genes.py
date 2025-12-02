"""
Script: comparar_listas_genes.py

Descripción:
    Compara dos listas de genes (manual y HPO) almacenadas en formato JSON.
    Muestra un resumen con el número total de genes, el tamaño de la intersección,
    los genes exclusivos de cada lista y un índice de solapamiento relativo.
    También genera un archivo de salida con los resultados detallados.
"""

import json
from pathlib import Path
import pandas as pd

# === Parámetros globales ===
INPUT_MANUAL_FILE = "lista_genes_manual.json"
INPUT_HPO_FILE = "lista_genes_hpo.json"
OUTPUT_COMPARISON_FILE = "comparacion_listas_genes.csv"

# === 1. Cargar listas de genes ===
def cargar_lista(ruta: str) -> set:
    """Carga una lista de genes desde un archivo JSON y la devuelve como conjunto."""
    if not Path(ruta).exists():
        raise FileNotFoundError(f"No se encontró el archivo: {ruta}")
    with open(ruta, "r") as f:
        return set(json.load(f))

genes_manual = cargar_lista(INPUT_MANUAL_FILE)
genes_hpo = cargar_lista(INPUT_HPO_FILE)

# === 2. Calcular métricas básicas ===
total_manual = len(genes_manual)
total_hpo = len(genes_hpo)
interseccion = genes_manual & genes_hpo
solo_manual = genes_manual - genes_hpo
solo_hpo = genes_hpo - genes_manual

porcentaje_solapamiento = round((len(interseccion) / len(genes_manual | genes_hpo)) * 100, 2)

# === 3. Mostrar resumen ===
print("🔍 Comparación de listas de genes")
print(f"----------------------------------")
print(f"Genes en lista manual: {total_manual}")
print(f"Genes en lista HPO:    {total_hpo}")
print(f"Genes en ambas:        {len(interseccion)}")
print(f"Solo en manual:        {len(solo_manual)}")
print(f"Solo en HPO:           {len(solo_hpo)}")
print(f"Solapamiento relativo: {porcentaje_solapamiento}%")

# === 4. Guardar resultados ===
df_resultados = pd.DataFrame({
    "categoria": ["manual_total", "hpo_total", "interseccion", "solo_manual", "solo_hpo"],
    "n_genes": [total_manual, total_hpo, len(interseccion), len(solo_manual), len(solo_hpo)]
})

df_resultados.to_csv(OUTPUT_COMPARISON_FILE, index=False)
print(f"\n✅ Resumen guardado en {OUTPUT_COMPARISON_FILE}")

# === 5. Guardar detalles en JSON opcionalmente ===
detalles = {
    "interseccion": sorted(interseccion),
    "solo_manual": sorted(solo_manual),
    "solo_hpo": sorted(solo_hpo),
    "porcentaje_solapamiento": porcentaje_solapamiento
}

with open("detalles_comparacion.json", "w") as f:
    json.dump(detalles, f, indent=4)
print("✅ Detalles guardados en detalles_comparacion.json")