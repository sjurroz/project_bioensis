#!/bin/bash
set -e

echo "======================================="
echo "   SETUP DEL PROYECTO"
echo "======================================="

BASE_DIR="$(pwd)"
VENV_DIR="$BASE_DIR/venv"
SOFTWARE_DIR="$BASE_DIR/software"   # se usa solo para compilaciones locales

# --------------------------------------
# Utilidad
# --------------------------------------
function msg() {
    echo -e "\n---------------------------------------"
    echo " $1"
    echo "---------------------------------------"
}

# --------------------------------------
# 1) Verificar o instalar Python
# --------------------------------------
msg "1) Verificando Python local"

if command -v python3 >/dev/null 2>&1; then
    PY=python3
elif command -v python >/dev/null 2>&1; then
    PY=python
else
    echo "❗ Python no está disponible. Instalando localmente…"

    mkdir -p "$SOFTWARE_DIR/python"
    cd "$SOFTWARE_DIR/python"

    PY_VERSION="3.11.9"
    PY_SRC="Python-$PY_VERSION.tgz"

    curl -LO "https://www.python.org/ftp/python/$PY_VERSION/$PY_SRC"
    tar -xzf "$PY_SRC"
    cd "Python-$PY_VERSION"

    ./configure --prefix="$SOFTWARE_DIR/python" --enable-optimizations
    make -j4
    make install

    PY="$SOFTWARE_DIR/python/bin/python3"
fi

echo "✓ Usando Python: $($PY --version)"
cd "$BASE_DIR"

# --------------------------------------
# 2) Crear y activar entorno virtual
# --------------------------------------
msg "2) Creando entorno virtual"

if [ ! -d "$VENV_DIR" ]; then
    $PY -m venv "$VENV_DIR"
fi

# Activación automática
source "$VENV_DIR/bin/activate"

# --------------------------------------
# 3) Actualizar pip
# --------------------------------------
msg "3) Actualizando pip"
pip install --upgrade pip setuptools wheel

# --------------------------------------
# 4) Instalar dependencias
# --------------------------------------
msg "4) Instalando librerías principales"

pip install \
    pandas \
    numpy \
    scipy \
    matplotlib \
    requests \
    networkx \
    pybind11 \
    seaborn

# --------------------------------------
# 5) Instalar GSEApy (ORA)
# --------------------------------------
msg "5) Instalando GSEApy (para ORA)"

pip install gseapy

echo "✓ GSEApy instalado"

# --------------------------------------
# 6) Infomap vía wheel (rápido)
# --------------------------------------
msg "6) Instalando Infomap (intento wheel)"

INFOMAP_OK=true
if pip install infomap; then
    echo "✓ Infomap instalado correctamente desde wheel"
else
    echo "⚠️ No hay wheel compatible. Intentando compilación local."
    INFOMAP_OK=false
fi

# --------------------------------------
# 7) Fallback: compilar Infomap localmente
# --------------------------------------
if [ "$INFOMAP_OK" = false ]; then
    msg "7) Compilando Infomap localmente (sin sudo)"

    mkdir -p "$SOFTWARE_DIR"
    cd "$SOFTWARE_DIR"

    if [ ! -d "infomap_src" ]; then
        git clone https://github.com/mapequation/infomap.git infomap_src
    fi

    cd infomap_src
    mkdir -p build
    cd build

    cmake .. -DCMAKE_INSTALL_PREFIX="$VENV_DIR"
    make -j4
    make install

    cd "$BASE_DIR"

    echo "✓ Infomap compilado e instalado dentro del entorno virtual"
fi

# --------------------------------------
# Final
# --------------------------------------
msg "SETUP COMPLETADO CON ÉXITO"

echo ""
echo "El entorno virtual ya está ACTIVADO."
echo "Puedes ejecutar ahora:"
echo "    ./run.sh"
echo ""