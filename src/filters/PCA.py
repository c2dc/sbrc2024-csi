import sys
import numpy as np
import pandas as pd
from PyQt5.QtWidgets import QApplication, QWidget
from pyqtgraph import PlotWidget
import pyqtgraph as pg
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
import argparse

# Definindo constantes para a leitura de dados CSI
CSI_DATA_COLUMNS = 52  # Número total de subportadoras usadas

# Inicializando array para armazenar os dados de CSI
csi_data_array = np.zeros([2197, CSI_DATA_COLUMNS], dtype=np.complex64)

class CsiDataGraphicalWindow(QWidget):
    def __init__(self, csi_data, csi_pca, var_exp, cum_var_exp):
        super().__init__()
        self.resize(1920, 1000)
        self.plotWidget = PlotWidget(self)
        self.plotWidget.setGeometry(0, 0, 1920, 1000)
        self.plotWidget.setYRange(-20, 30)
        self.plotWidget.addLegend()

        # Exibindo os componentes principais no gráfico
        self.plotWidget.plot(csi_pca[:, 0], pen=(255, 0, 0))
        self.plotWidget.plot(csi_pca[:, 1], pen=(0, 255, 0))
        self.plotWidget.plot(csi_pca[:, 2], pen=(0, 0, 255))
        self.plotWidget.plot(csi_pca[:, 3], pen=(255, 0, 255))

        # Plotando a variância explicada
        plt.figure(figsize=(10, 5))
        plt.bar(range(1, len(var_exp) + 1), var_exp, alpha=0.5, align='center', label='Variância explicada individual')
        plt.step(range(1, len(cum_var_exp) + 1), cum_var_exp, where='mid', label='Variância explicada acumulada')
        plt.ylabel('Razão da Variância Explicada')
        plt.xlabel('Componentes Principais')
        plt.legend(loc='best')
        plt.tight_layout()
        plt.show()

def read_csi_data_from_csv(file_path):
    df = pd.read_csv(file_path, skip_blank_lines=True)
    for i, row in df.iterrows():
        csi_str = row['data'].strip('[]')
        csi_values = np.fromstring(csi_str, sep=', ', dtype=np.float32)
        csi_complex = csi_values[::2] + 1j * csi_values[1::2]
        csi_data_array[:-1] = csi_data_array[1:]
        csi_data_array[-1, :] = csi_complex[:CSI_DATA_COLUMNS]

    # Aplicando PCA aos dados CSI
    scaler = StandardScaler()
    csi_data_scaled = scaler.fit_transform(np.abs(csi_data_array))
    pca = PCA()
    csi_pca = pca.fit_transform(csi_data_scaled)
    var_exp = pca.explained_variance_ratio_
    cum_var_exp = np.cumsum(var_exp)

    return csi_data_array, csi_pca, var_exp, cum_var_exp

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Read CSI data from a CSV file and display it graphically")
    parser.add_argument('-f', '--file', dest='file_path', action='store', required=True,
    help="Path to the CSV file containing CSI data")
    args = parser.parse_args()
    app = QApplication(sys.argv)
    csi_data_array, csi_pca, var_exp, cum_var_exp = read_csi_data_from_csv(args.file_path)
    window = CsiDataGraphicalWindow(csi_data_array, csi_pca, var_exp, cum_var_exp)
    window.show()
    sys.exit(app.exec_())

