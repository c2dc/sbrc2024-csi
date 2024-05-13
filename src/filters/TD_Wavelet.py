import sys
import pandas as pd
import numpy as np
import pywt
from PyQt5.QtWidgets import QApplication, QWidget
from pyqtgraph import PlotWidget
import argparse

# Definindo constantes para a leitura de dados CSI
CSI_DATA_COLUMNS = 52  # Número total de subportadoras usadas

# Inicializando array para armazenar os dados de CSI
csi_data_array = np.zeros([2197, CSI_DATA_COLUMNS], dtype=np.complex64)

class CsiDataGraphicalWindow(QWidget):
    def __init__(self, csi_data):
        super().__init__()
        self.resize(1920, 1080)
        self.plotWidget = PlotWidget(self)
        self.plotWidget.setGeometry(0, 0, 1920, 1080)
        self.plotWidget.setYRange(5, 105)  # Ajuste conforme necessário
        self.plotWidget.addLegend()

        # Aplicando a Transformada Discreta de Wavelet
        wavelet = 'db1'  # Usando Daubechies 1
        level = 3  # Nível de decomposição

        self.csi_wavelet_array = np.apply_along_axis(
            lambda x: np.abs(pywt.wavedec(x, wavelet, level=level)[0]), 0, csi_data)

        # Plotando os dados processados
        for i in range(CSI_DATA_COLUMNS):
            self.plotWidget.plot(self.csi_wavelet_array[:, i], name=str(i))

def read_csi_data_from_csv(file_path):
    df = pd.read_csv(file_path, skip_blank_lines=True)
    for i, row in df.iterrows():
        csi_str = row['data'].strip('[]')
        csi_values = np.fromstring(csi_str, sep=', ', dtype=np.float32)
        csi_complex = csi_values[::2] + 1j * csi_values[1::2]
        csi_data_array[:-1] = csi_data_array[1:]
        csi_data_array[-1, :] = csi_complex[:CSI_DATA_COLUMNS]

    return np.abs(csi_data_array)  # Retorna a magnitude do sinal

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Read CSI data from a CSV file and display it graphically using DWT")
    parser.add_argument('-f', '--file', dest='file_path', action='store', required=True,
                        help="Path to the CSV file containing CSI data")
    args = parser.parse_args()

    app = QApplication(sys.argv)
    csi_data = read_csi_data_from_csv(args.file_path)
    window = CsiDataGraphicalWindow(csi_data)
    window.show()
    sys.exit(app.exec_())
