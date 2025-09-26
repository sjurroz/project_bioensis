#!/usr/bin/env Rscript

# Cargar librerías necesarias
suppressPackageStartupMessages({
  library(optparse)
  library(igraph)
})

# Definir las opciones de línea de comandos
option_list <- list(
  make_option(c("-i", "--input_file"), type = "character", default = NULL,
              help = "Input file with graph edges"),
  
  make_option(c("-g", "--graph_file"), type = "character", default = NULL,
              help = "Output file with network graph"),
  
  make_option(c("-d", "--dict_file"), type = "character", default = NULL,
              help = "File to translate gene symbol to ensembl protein"),
  
  make_option(c("-G", "--gene_subset"), type = "character", default = NULL,
              help = "File with gene list associated to HPO")
)

# Parsear opciones
opt <- parse_args(OptionParser(option_list = option_list))

# Leer los archivos de entrada
net_table  <- read.table(opt$input_file, sep = "\t", header = TRUE)
gene_list  <- read.table(opt$gene_subset, sep = "\t", header = TRUE)
dict_gene  <- read.table(opt$dict_file, sep = "\t", header = FALSE)

# Mapear los genes de la lista con los identificadores de la red
match_vector <- match(gene_list$name, dict_gene$V2)
gene_list <- dict_gene$V1[match_vector]
gene_list <- gene_list[!is.na(gene_list)]   # quitar NAs

# Crear el grafo a partir de los edges
net <- graph_from_data_frame(d = net_table)

# Extraer los nodos que pertenecen a la lista de genes
nodes_in_graph <- match(gene_list, V(net)$name)
nodes_in_graph <- nodes_in_graph[!is.na(nodes_in_graph)]
gene_list <- V(net)$name[nodes_in_graph]

# Construir subgrafo únicamente con esos genes
net <- subgraph(net, gene_list)

# Mostrar información del grafo
print(net)  # primera línea da número de nodos y aristas
print(transitivity(net))

# Exportar gráfico a PDF
pdf(file = opt$graph_file)
plot(
  net,
  vertex.color = "orange",
  vertex.size = 5,
  vertex.label = NA,
  edge.width = 0.5,
  main = "Nicely Layout"
)
dev.off()