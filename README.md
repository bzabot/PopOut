# PopOut, MCTS e Decision Trees

Projeto da unidade curricular de Inteligencia Artificial 2025/2026.

O ficheiro principal de entrada e:

- `PopOut_MCTS_DecisionTrees.ipynb`: notebook principal do trabalho. Resume a implementacao do jogo PopOut, MCTS, Decision Tree ID3, dataset PopOut e demonstracao dos modos de jogo.

Notebooks complementares:

- `iris_id3_notebook.ipynb`: experiencia com o dataset Iris, discretizacao e avaliacao da Decision Tree ID3.
- `mcts_quality_time_comparison.ipynb`: comparacao experimental entre MCTS base e MCTS com heuristicas, incluindo qualidade e tempo medio por jogada.

## Estrutura

- `src/pop_out.py`: regras do jogo PopOut, movimentos `drop`/`pop`, vitorias e empates.
- `src/play_popout.py`: interface de jogo no terminal com humano, random, MCTS e Decision Tree.
- `src/mcts/`: implementacoes do MCTS, incluindo versao base, heuristica e paralela.
- `src/decision_tree/`: implementacao propria do ID3, metricas de entropia e nos da arvore.
- `src/popout_decision_tree/`: treino, uso e geracao de datasets para a Decision Tree do PopOut.
- `src/popout_decision_tree/datasets/Tree.svg`: visualizacao exportada da arvore treinada para PopOut.
- `src/popout_decision_tree/datasets/complete_popout_dataset.csv`: dataset final usado para treinar a Decision Tree do PopOut.
- `outputs/`: resultados e graficos das experiencias com MCTS.
- `Apresentacao_TP_IA.pdf`: slides da apresentacao.
- `IA_2526_Project.pdf`: enunciado do projeto.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Executar

Abrir o notebook principal:

```bash
jupyter notebook PopOut_MCTS_DecisionTrees.ipynb
```

Exemplos de jogo no terminal:

```bash
python -m src.play_popout --red human --blue human
python -m src.play_popout --red human --blue mcts --mcts-iterations 500
python -m src.play_popout --red mcts --blue dt --mcts-iterations 500 --delay 0.1
```

Algumas celulas de treino/geracao de dados estao desligadas por padrao porque podem demorar bastante.
