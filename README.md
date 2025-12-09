
# 🧬💻 Análisis de la Esclerosis Lateral Amiotrófica mediante Biología de Sistemas


Este proyecto realiza un análisis integral de la Esclerosis Lateral Amiotrófica (ELA) utilizando **biología de sistemas**.
El flujo de trabajo propuesto genera redes de proteínas, realiza clustering, análisis de topología de red y análisis funcional de los genes asociados con ELA.

---

## 🎯 Objetivos Principales

- Generar redes de interacción proteína-proteína relacionadas con ELA
- Identificar módulos/clusters en las redes biológicas
- Realizar análisis de enriquecimiento funcional (GO, KEGG, Reactome) en los clusters identificados
- Comparar múltiples listas de genes relevantes para ELA, ya sea de forma manual o utilizando GO.

---

## ⛓️ Descripción general del flujo
El proyecto implementa un pipeline automatizado que procesa datos de genes asociados con la ELA a través de cinco etapas secuenciales.

1. **Obtención de datos iniciales**: El pipeline obtiene listas de genes de dos fuentes distintas:

- Genes asociados con la ELA en la Human Phenotype Ontology (HPO).
- Genes seleccionados a partir de una revisión bibliográfica manual.

2. **Generación de redes:** El sistema consulta la API de STRING para obtener las interacciones proteína-proteína entre los genes de entrada.
Filtra estas interacciones por diferentes umbrales de confianza, obteniendo una red por cada valor:

- Score 300 (confianza baja)
- Score 700 (confianza media)
- Score 900 (confianza alta)

3. **Análisis topológico:** El pipeline calcula métricas estructurales de cada red, incluyendo:

- Propiedades globales: densidad, diámetro, coeficiente de clustering
- Métricas de centralidad: grado, betweenness, closeness

**Clustering y detección de módulos:** El sistema ejecuta tres algoritmos de clustering:
- Fast Greedy Modularity (optimiza la modularidad)
- Edge Betweenness (realiza divisiones jerárquicas)
- Infomap (basado en teoría de la información)

4. **Análisis funcional:** El pipeline realiza un análisis de sobrerrepresentación (ORA)
para cada cluster identificado, utilizando 3 bases de datos como referencia:

- _Gene Ontology (procesos biológicos)_: forma parte de la Gene Ontology (GO), y describe los procesos biológicos en los que participan los genes.
- _KEGG_: representa las rutas metabólicas y de señalización del organismo humano, mostrando cómo interactúan los genes y proteínas dentro de sistemas biológicos.
- _Reactome_: recopila reacciones metabólicas y vías moleculares del genoma humano, con anotaciones curadas manualmente por expertos a partir de evidencia experimental.

5. **Síntesis de resultados:** El sistema genera tablas comparativas considerando las distintas combinaciones de parámetros propuestas en cada etapa:
- Modo de extracción de genes (HPO, manual)
- Umbral de confianza en las interacciones (300, 700, 900)
- Algoritmo de clustering (fast greedy, edge betweeness, infomap)

Esto facilita la interpretación y comparación del impacto de las diferentes configuraciones.

---

## 🗂️ Estructura del Proyecto

El repositorio se organiza de la siguiente manera: 

```
project_bioensis/
├── code/                                   # Codigo fuente principal
│   ├── scripts/                            # Scripts del pipeline
│   ├── setup.sh                            # Script para instalación de dependencias
│   └── run.sh                              # Script principal para ejecutar el pipeline
│
├── genes/                                  # Genes de entrada (lista manual)
│
├── report/                                 # Artículo del proyecto
│
├── results/                                # Resultados de ejecución
│   │
│   ├── redes/                              # Subdirectorios de redes por tipo y score de interacción
│   │   │
│   │   ├── hpo_score300/
│   │   │   ├── clustering/                 # Resultados por algoritmo de clustering
│   │   │   ├── funcional/                  # Resultados del ORA por cluster y base de datos
│   │   │   ├── topologia/                  # Métricas topológicas de la red
│   │   │   ├── red_hpo_score300.png        # Representación gráfica de la red
│   │   │   └── red_hpo_score300.txt        # Representación de nodos e interacciones
│   │   │
│   │   ├── hpo_score700/
│   │   ├── hpo_score900/
│   │   ├── manual_score300/
│   │   ├── manual_score700/
│   │   └── manual_score900/
│   │
│   ├── resumen_clustering_hpo.csv          # Tabla resumen de clustering y enriquecimiento para redes HPO
│   └── resumen_clustering_manual.csv       # Tabla resumen de clustering y enriquecimiento para redes manual
│
└── README.md
```

---

## 🔧 Instalación y ejecución

Para ejecutar correctamente el proyecto se requiere el siguiente entorno básico:

- Python 3.8+
- Bash (Linux/macOS) o compatible (Git Bash en Windows)
- Git

### 1. Clonar el repositorio

Clonar este repositorio usando `git`:

```bash
git clone "https://github.com/sjurroz/project_bioensis.git"
```

### 2. Configuración del entorno

Ejecutar el script `setup.sh` para crear un entorno virtual de Python
e instalar todas las dependencias necesarias:

```bash
cd code/
bash setup.sh
```

Con esto se instalan automaticamente los siguientes dependencias:

- `pandas` - Manipulación y análisis de datos
- `numpy` - Computación numérica
- `scipy` - Funciones científicas
- `matplotlib` - Visualización de gráficos
- `requests` - Solicitudes HTTP (para consultar APIs)
- `networkx` - Análisis y visualización de redes
- `seaborn` - Visualización estadística avanzada
- `gseapy` - Análisis de enriquecimiento funcional (ORA)
- `infomap` - Algoritmo de clustering basado en teoría de información

### 3. Ejecución del pipeline

Ejecutar el script `run.sh` para generar todos los resultados:

```bash
cd code/
bash run.sh
```

> [!NOTE]
> El score de confianza (300/700/900) afecta significativamente el tamaño y composición de la red

> [!NOTE]
> Requiere conexión a internet para consultar APIs (STRING, HPO, GO)

> [!IMPORTANT]
> La ejecución completa del pipeline puede tardar hasta 10 minutos debido al
> extenso número de combinaciones propuesto.

---

## 📊 Resultados esperados

### Contenido generado por cada red

Cada red analizada genera un conjunto coherente y trazable de salidas, todas ubicadas dentro de
`results/redes/<nombre_red_score>/`.

- **Clustering por algoritmo**  
  Carpeta `clustering/` con los resultados estructurados para cada método (Infomap, Fast Greedy, Edge Betweenness).

- **Análisis funcional (ORA)**  
  Carpeta `funcional/` con los términos enriquecidos por cluster y por base de datos, listos para interpretación biológica.

- **Topología de la red**  
  Carpeta `topologia/` con las métricas globales de la red (grado, modularidad, centralidad, etc.).

- **Representaciones visuales**  
  - `*.png`: visualización de la red usando `NetworkX`.  
  - `*.txt`: listado legible de nodos e interacciones.



### Tablas resumen comparativas

Además de las salidas específicas por red, el pipeline genera tablas resumen en el directorio raíz de `results/`:

- `resumen_clustering_hpo.csv`  
- `resumen_clustering_manual.csv`

Estas tablas condensan, de forma simple y manejable:

- número total de clusters,  
- tamaño medio de los clusters,  
- número de términos GO enriquecidos por cluster o en total.

Funcionan como un filtro inicial para identificar qué combinación red–score–algoritmo es más coherente y merece un análisis biológico más profundo.

---

## 👥 Autores

- Santiago Juarroz Surballe (santiagojuarroz@uma.es)
- Gabriela Milenova Yordanova (gamy-@uma.es)
- Maga C. Chediack (chediackmaga@uma.es)
- Sebastián Rozenblum (srozenblum@uma.es)

**Institución**: Universidad de Málaga  
**Programa**: Grado en Ingenieria de la Salud