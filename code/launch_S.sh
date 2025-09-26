#!/bin/bash
set -euo pipefail

# Definir librería local de R
export R_LIBS_USER=./R_LIBS

# Crear carpetas necesarias
mkdir -p ../results/data

# Descargar la red de interacciones (STRINGDB links)
wget "https://stringdb-downloads.org/download/protein.links.v12.0/9606.protein.links.v12.0.txt.gz" \
     -O ../results/data/string.txt.gz

gunzip -f ../results/data/string.txt.gz

# Filtrar interacciones con score > 900
awk -F' ' '{ if ($3 > 900) print $1 "\t" $2 "\t" $3 }' \
    ../results/data/string.txt > ../results/data/string_network.txt

# Descargar aliases
wget "https://stringdb-downloads.org/download/protein.aliases.v12.0/9606.protein.aliases.v12.0.txt.gz" \
     -O ../results/data/aliases.txt.gz

gunzip -f ../results/data/aliases.txt.gz

# Extraer diccionario de genes (HGNC symbol)
grep 'Ensembl_HGNC_symbol' ../results/data/aliases.txt \
    | cut -f 1,2 > ../results/data/string_dict.txt

# Descargar anotaciones de HPO
wget "https://ontology.jax.org/api/network/annotation/HP:0000098/download/gene" \
     -O ../results/data/hpo_query.txt

cut -f 2 ../results/data/hpo_query.txt | tr -d ' ' > ../results/data/hpo_gene.txt

# Ejecutar el análisis en R
./analyse_net_S.R \
  -i ../results/data/string_network.txt \
  -g ../results/net.pdf \
  -G ../results/data/hpo_gene.txt \
  -d ../results/data/string_dict.txt