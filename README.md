
# BioEnsIS: Análisis de Esclerosis Lateral Amiotrófica mediante Biología de Sistemas

## 📋 Descripción

Este proyecto realiza un análisis integral de la Esclerosis Lateral Amiotrófica (ELA) utilizando **biología de sistemas**. El pipeline genera redes de proteínas, realiza clustering, análisis de topología de red y análisis funcional de los genes asociados con ELA.

## 🎯 Objetivos Principales

- Generar redes de interacción proteína-proteína relacionadas con ELA
- Identificar módulos/clusters en las redes biológicas
- Realizar análisis de enriquecimiento funcional (GO, KEGG) en los clusters identificados
- Comparar múltiples listas de genes relevantes para ELA, ya sea de forma manual o utilizando GO.

## ⛓️ Descripción general del flujo
El proyecto implementa un pipeline automatizado que procesa datos de genes asociados con Esclerosis Lateral Amiotrófica (ELA) a través de cinco etapas secuenciales.

**Obtención de datos iniciales**: El pipeline obtiene listas de genes de dos fuentes distintas:

- Genes asociados con ELA en la Human Phenotype Ontology (HPO)
- Una lista de genes seleccionados manualmente

Estos genes sirven como punto de partida para todo el análisis.

**Generación de redes:** El sistema consulta la API de STRING para obtener las interacciones proteína-proteína entre los genes de entrada. Filtra estas interacciones por diferentes umbrales de confianza:

- Score 300 (confianza baja)
- Score 700 (confianza media)
- Score 900 (confianza alta)
   
Cada red resultante se visualiza y se exporta en formato GraphML para análisis posteriores.

**Análisis topológico:** El pipeline calcula métricas estructurales de cada red, incluyendo:

- Propiedades globales: densidad, diámetro, coeficiente de clustering
- Métricas de centralidad: grado, betweenness, closeness

**Clustering y detección de módulos:** El sistema ejecuta tres algoritmos de detección de comunidades en paralelo:
- Fast Greedy Modularity (optimiza la modularidad)
- Edge Betweenness (realiza divisiones jerárquicas)
- Infomap (basado en teoría de la información)
Estos algoritmos identifican módulos o clusters biológicamente significativos dentro de cada red.

**Análisis funcional:** El pipeline realiza un análisis de enriquecimiento (ORA) para cada cluster identificado, evaluando:

- Términos en Gene Ontology (procesos biológicos)
- Funciones moleculares
- Vías KEGG
Esto identifica qué procesos biológicos son característicos de cada módulo.

**Síntesis de resultados:** El sistema genera tablas comparativas considerando:
- Diferentes algoritmos de clustering
- Múltiples modos de análisis (HPO vs manual)
- Diversos umbrales de confianza (300, 700, 900)
Esto facilita la interpretación y comparación del impacto de las diferentes configuraciones.

## 🗂️ Estructura del Proyecto
El proyecto esta organizado de la siguiente forma para tener un acceso mas intuitivo y estructurado.
```
project_bioensis/
├── code/
│   ├── scripts/
│   │   ├── pipeline.py
│   │   ├── generar_red.py
│   │   ├── clustering.py
│   │   ├── analizar_topologia_red.py
│   │   ├── analisis_funcional_clusters.py
│   │   ├── resumen_clustering.py
│   │   └── paths.py
│   ├── setup.sh
│   └── run.sh
├── genes/
│   ├── comparacion_listas_genes.csv
│   ├── lista_genes_hpo.json
│   └── lista_genes_manual.json
├── report/
│   ├── bibliography/
│   │   ├── references.bib
│   │   └── TFM2.bib
│   ├── figures/
│   │   ├── COMPARATIVA DE ALGORITMOS DE AGRUPAMIENTO.png
│   │   ├── Diagrama de flujo BioSis.drawio.png
│   │   ├── EDGE BETWEENNESS HPO.png
│   │   ├── EDGE BETWEENNESS MANUAL.png
│   │   ├── edge_betweenness_hpo_score700.png
│   │   ├── edge_betweenness_manual_score700.png
│   │   ├── Sequencing_Cost_per_Genome_May2020.jpg
│   │   └── Sequencing_Cost_per_Megabase_May2020.jpg
│   ├── tex_files/
│   │   ├── anexo.tex
│   │   ├── conclusiones.tex
│   │   ├── discusion.tex
│   │   ├── introduction.tex
│   │   ├── material_methods.tex
│   │   └── resultados.tex
│   ├── bibliography.bib
│   ├── bmc-mathphys.bst
│   ├── bmcart-biblio.sty
│   ├── bmcart.cls
│   ├── report.aux
│   ├── report.bbl
│   ├── report.blg
│   ├── report.tex
│   ├── spbasic.bst
│   └── vancouver.bst
├── results/
└── README.md
```


## 🔧 Instalación

### Requisitos previos
- Python 3.8+
- Bash (Linux/macOS) o compatible (Git Bash en Windows)
- Git

### Configuración del entorno

```bash
cd code/
bash setup.sh