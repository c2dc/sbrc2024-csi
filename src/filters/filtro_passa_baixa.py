import sys
import csv
import numpy as np
import pandas as pd
import scipy.signal as signal
from PyQt5.QtWidgets import QApplication, QWidget
from pyqtgraph import PlotWidget
import pyqtgraph as pg
import argparse

# Constantes
CSI_DATA_COLUMNS = 52  # Número total de subportadoras usadas
FS = 110  # Taxa de amostragem em Hz

# Inicializando array para armazenar os dados de CSI
csi_data_array = np.zeros([1000, CSI_DATA_COLUMNS], dtype=np.complex64)

class CsiDataGraphicalWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.resize(1920, 1080)
        self.plotWidget = PlotWidget(self)
        self.plotWidget.setGeometry(0, 0, 1920, 1080)
        self.plotWidget.setYRange(0, 45)
        self.plotWidget.addLegend()

        # Convertendo os dados CSI para a forma de magnitude
        self.csi_magnitude_array = np.abs(csi_data_array)
        self.curve_list = []

        for i in range(CSI_DATA_COLUMNS):
            curve = self.plotWidget.plot(self.csi_magnitude_array[:, i], name=str(i))
            self.curve_list.append(curve)

    def update_data(self):
        self.csi_magnitude_array = np.abs(csi_data_array)
        for i in range(CSI_DATA_COLUMNS):
            self.curve_list[i].setData(self.csi_magnitude_array[:, i])

def low_pass_filter(data, cutoff, fs, order=5):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = signal.butter(order, normal_cutoff, btype='low', analog=False)
    y = signal.lfilter(b, a, data)
    return y

def read_csi_data_from_csv(file_path):
    df = pd.read_csv(file_path, skip_blank_lines=True)
    for i, row in df.iterrows():
        csi_str = row['data'].strip('[]')
        csi_values = np.fromstring(csi_str, sep=', ', dtype=np.float32)
        csi_complex = csi_values[::2] + 1j * csi_values[1::2]
        csi_complex_filtered = low_pass_filter(csi_complex, cutoff=30, fs=FS, order=6)
        csi_data_array[:-1] = csi_data_array[1:]
        csi_data_array[-1, :] = np.abs(csi_complex_filtered[:CSI_DATA_COLUMNS])

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Read CSI data from a CSV file and display it graphically")
    parser.add_argument('-f', '--file', dest='file_path', action='store', required=True,
                        help="Path to the CSV file containing CSI data")
    args = parser.parse_args()

    app = QApplication(sys.argv)
    read_csi_data_from_csv(args.file_path)
    window = CsiDataGraphicalWindow()
    window.show()
    sys.exit(app.exec_())
