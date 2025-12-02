"""
Módulo: paths.py

Descripción:
    Define rutas globales del proyecto y garantiza que la estructura
    base de directorios bajo `resultados/` exista siempre.

Estructura mínima creada automáticamente:

    resultados/
        redes/

El resto de subdirectorios (por modo, score, clustering, funcional, etc.)
se crean en los módulos correspondientes usando mkdir(parents=True, exist_ok=True).
"""

from pathlib import Path

# Ruta raíz del proyecto (directorio `codigo/`)
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Carpeta principal de resultados
RESULTADOS_DIR = PROJECT_ROOT / "results"

# Subdirectorio base donde se guardan las redes
REDES_DIR = RESULTADOS_DIR / "redes"


def asegurar_estructura_resultados() -> None:
    """
    Crea la estructura básica de resultados necesaria para que cualquier módulo
    pueda escribir sin errores, asumiendo que al inicio solo existe `resultados/`
    (o ni eso).
    """
    RESULTADOS_DIR.mkdir(parents=True, exist_ok=True)
    REDES_DIR.mkdir(parents=True, exist_ok=True)


# Se ejecuta al importar el módulo
asegurar_estructura_resultados()

# Ruta a la lista de genes manual
LISTA_GENES_MANUAL = PROJECT_ROOT / "genes" / "lista_genes_manual.json"