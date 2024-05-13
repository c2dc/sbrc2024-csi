import os
import pandas as pd

input_dir = './'
output_dir = './filtered_output/'

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

for filename in os.listdir(input_dir):
    if filename.endswith('.csv'):
        file_path = os.path.join(input_dir, filename)
        df = pd.read_csv(file_path)

        # Filtrar colunas rssi, rotulo e que começam com 'amp'
        cols_to_keep = [col for col in df.columns if col.startswith('amp') or col == 'rssi' or col == 'rotulo']

        # Criar um novo DataFrame com apenas as colunas desejadas
        filtered_df = df[cols_to_keep]

        # Salvar o DataFrame resultante no diretório de saída
        output_file_path = os.path.join(output_dir, filename)
        filtered_df.to_csv(output_file_path, index=False)

print("Processamento concluído. Arquivos filtrados salvos em:", output_dir)
