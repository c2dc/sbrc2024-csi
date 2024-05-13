import sys
import numpy as np
import pandas as pd
from scipy.signal import hilbert
from PyQt5.QtWidgets import QApplication, QWidget
from pyqtgraph import PlotWidget
import argparse

# Constantes
CSI_DATA_COLUMNS = 52  # Número total de subportadoras usadas

class CsiDataGraphicalWindow(QWidget):
    def __init__(self, csi_data):
        super().__init__()
        self.resize(1280, 720)
        self.plotWidget = PlotWidget(self)
        self.plotWidget.setGeometry(0, 0, 1280, 720)
        self.plotWidget.setYRange(-0.5, 3)  # Ajuste conforme necessário
        self.plotWidget.addLegend()

        # Aplicando a transformada de Hilbert
        self.csi_analytic_array = np.apply_along_axis(lambda x: hilbert(x), 0, csi_data)
        self.curve_list = []

        for i in range(CSI_DATA_COLUMNS):
            curve = self.plotWidget.plot(np.abs(self.csi_analytic_array[:, i]), name=str(i))
            self.curve_list.append(curve)

def read_csi_data_from_csv(file_path):
    df = pd.read_csv(file_path, skip_blank_lines=True)
    csi_data_array = np.zeros([len(df), CSI_DATA_COLUMNS], dtype=np.float64)
    for i, row in df.iterrows():
        csi_str = row['data'].strip('[]')
        csi_values = np.fromstring(csi_str, sep=', ', dtype=np.float32)
        csi_data_array[i, :] = csi_values[:CSI_DATA_COLUMNS * 2:2]  # Usando apenas a parte real
    return csi_data_array

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Read CSI data from a CSV file and process it using Hilbert Transform")
    parser.add_argument('-f', '--file', dest='file_path', action='store', required=True,
                        help="Path to the CSV file containing CSI data")
    args = parser.parse_args()

    app = QApplication(sys.argv)
    csi_data = read_csi_data_from_csv(args.file_path)
    window = CsiDataGraphicalWindow(csi_data)
    window.show()
    sys.exit(app.exec_())
