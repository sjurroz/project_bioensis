#!/bin/bash
set -e

echo "======================================="
echo " Ejecutando pipeline completo de redes"
echo "======================================="

BASE_DIR="$(pwd)"
VENV_DIR="$BASE_DIR/venv"

# Activar entorno virtual
if [ -f "$VENV_DIR/bin/activate" ]; then
    source "$VENV_DIR/bin/activate"
else
    echo "❌ ERROR: no existe el entorno virtual en venv/"
    echo "Ejecuta primero: ./setup.sh"
    exit 1
fi

# Ejecutar pipeline desde el directorio scripts/
python scripts/pipeline.py
EXIT_CODE=$?

echo "======================================="
if [ $EXIT_CODE -eq 0 ]; then
    echo " ✓ Pipeline completado sin errores."
else
    echo " ❌ ERROR: pipeline finalizó con errores."
    echo " Código de salida: $EXIT_CODE"
fi
echo "======================================="