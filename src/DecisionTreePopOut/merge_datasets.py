import pandas as pd
import glob


def merge_datasets():
    arquivos_csv = glob.glob("MCTS_popout_dataset*.csv")

    print(len(arquivos_csv))

    lista_de_dfs = []

    for arquivo in arquivos_csv:
        df = pd.read_csv(arquivo)
        lista_de_dfs.append(df)

    dataset_completo = pd.concat(lista_de_dfs, ignore_index=True)
    tamanho_original = len(dataset_completo)
    dataset_completo = dataset_completo.drop_duplicates()
    tamanho_novo = len(dataset_completo)

    dataset_completo.to_csv("MCTS_popout_dataset.csv", index=False)

    print(f"Total lines read: {tamanho_original}")
    print(f"Duplicates: {tamanho_original - tamanho_novo}")
    print(f"Unique lines to train the DT: {tamanho_novo}")


if __name__ == "__main__":
    merge_datasets()