# ID3 - Iris Dataset

Este conjunto de ficheiros implementa uma árvore de decisão ID3 para o dataset Iris.

## Ficheiros

- `discretizer.py`  
  Contém funções para transformar atributos numéricos em categorias discretas (`bin_0`, `bin_1`, etc.), usando `equal_width` ou `equal_frequency`.

- `metrics.py`  
  Contém as métricas usadas pelo ID3: entropia, entropia condicional, ganho de informação e escolha do melhor atributo.

- `id3.py`  
  Contém a implementação principal da árvore ID3: criação dos nós, construção recursiva da árvore, previsão de novos exemplos e impressão da árvore em texto.

- `visualizer.py`  
  Converte a árvore ID3 para formato Graphviz, permitindo visualizar a árvore de forma gráfica.

- `iris_id3_notebook.ipynb`  
  Notebook com o fluxo completo: carregamento dos dados, discretização, treino da árvore, visualização e avaliação no conjunto de teste.

## Nota

A discretização é usada para lidar com os valores numéricos do dataset Iris e ajudar a manter a árvore mais simples.
