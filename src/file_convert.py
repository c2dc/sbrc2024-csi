import os
import pandas as pd
import numpy as np
import cmath

input_dir = './'
output_dir = './out/'

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

csv_files = [f for f in os.listdir(input_dir) if f.endswith('.csv')]
cols_to_remove = ['type', 'seq', 'timestamp', 'taget_seq', 'taget', 'mac', 'rate', 'sig_mode', 'mcs', 'cwb', 'smoothing', 'not_sounding', 'aggregation', 'stbc', 'fec_coding', 'sgi', 'noise_floor', 'ampdu_cnt', 'channel_primary', 'channel_secondary', 'local_timestamp', 'ant', 'sig_len', 'rx_state', 'len', 'first_word_invalid'] 


df_camara, df_lab, df_tudo = pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

for file in csv_files:
    df = pd.read_csv(os.path.join(input_dir, file))
    df = df.drop(columns=cols_to_remove)

    def process_csi(row):
        numbers = list(map(int, row[1:-1].split(',')))[2:]
        amps, phases = [], []
        for i in range(0, len(numbers), 2):
            complex_num = complex(numbers[i], numbers[i + 1])
            amp, phase = cmath.polar(complex_num)
            amps.append(amp)
            phases.append(phase)
        return amps + phases

    new_columns = ['amp' + str(i) for i in range(2, 53)] + ['fase' + str(i) for i in range(2, 53)]
    csi_processed = df['data'].apply(process_csi)
    csi_df = pd.DataFrame(csi_processed.tolist(), columns=new_columns)

    df = pd.concat([df, csi_df], axis=1)
    df = df.drop(columns=['data'])

    df['rotulo'] = 'ofensivo' if 'Offensive' in file else 'neutro'
    #df['nome_arquivo'] = file

    df.to_csv(os.path.join(output_dir, file), index=False)

    df_tudo = pd.concat([df_tudo, df])
    if 'Câmara' in file:
        df_camara = pd.concat([df_camara, df])
    elif 'Lab' in file:
        df_lab = pd.concat([df_lab, df])

df_camara.to_csv(os.path.join(output_dir, 'Camara.csv'), index=False)
df_lab.to_csv(os.path.join(output_dir, 'Lab.csv'), index=False)
df_tudo.to_csv(os.path.join(output_dir, 'Tudo.csv'), index=False)