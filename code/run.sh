#!/bin/bash
set -e

# ==============================
# Comprobación: NO ejecutar como root
# ==============================
if [ "$(id -u)" -eq 0 ]; then
    echo "❌ ERROR: este script no puede ejecutarse como root."
    echo "No se permite asumir permisos de administrador."
    exit 1
fi

echo "======================================="
echo " Ejecutando pipeline completo de redes"
echo "======================================="

BASE_DIR="$(pwd)"
VENV_DIR="$BASE_DIR/venv"

# Detectar Windows (Git Bash, MSYS, Cygwin)
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
    ACTIVATE_PATH="$VENV_DIR/Scripts/activate"
else
    ACTIVATE_PATH="$VENV_DIR/bin/activate"
fi

if [ ! -f "$ACTIVATE_PATH" ]; then
    echo "❌ ERROR: no existe el entorno virtual esperado:"
    echo "   $ACTIVATE_PATH"
    echo "Ejecuta primero: ./setup.sh"
    exit 1
fi

source "$ACTIVATE_PATH"

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