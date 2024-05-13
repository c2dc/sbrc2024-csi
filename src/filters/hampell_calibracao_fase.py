import sys
import numpy as np
import pandas as pd
from PyQt5.QtWidgets import QApplication, QWidget
from pyqtgraph import PlotWidget
import argparse

# Definindo constantes para a leitura de dados CSI
CSI_DATA_COLUMNS = 52  # Número total de subportadoras usadas

# Inicializando array para armazenar os dados de CSI
csi_data_array = np.zeros([2197, CSI_DATA_COLUMNS], dtype=np.complex64)

class CsiDataGraphicalWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.resize(1920, 1080)
        self.plotWidget = PlotWidget(self)
        self.plotWidget.setGeometry(0, 0, 1920, 1080)
        self.plotWidget.setYRange(0, 50)
        self.plotWidget.addLegend()

        # Convertendo os dados CSI para a forma de magnitude
        self.csi_magnitude_array = np.abs(csi_data_array)
        self.curve_list = []

        for i in range(CSI_DATA_COLUMNS):
            curve = self.plotWidget.plot(self.csi_magnitude_array[:, i], name=str(i))
            self.curve_list.append(curve)

def hampel_filter_for_series(s, window_size):
    rolling_median = s.rolling(window=2 * window_size, center=True).median()
    mad = lambda x: np.fabs(x - x.median()).median()
    deviation = np.fabs(s - rolling_median)
    threshold = 3 * s.rolling(window=2 * window_size, center=True).apply(mad)
    outlier_idx = deviation > threshold
    s[outlier_idx] = rolling_median[outlier_idx]
    return s

def phase_calibration(csi_complex):
    # Calibração de fase
    angle = np.unwrap(np.angle(csi_complex))
    angle_diff = np.diff(angle, axis=0)
    angle_diff = np.vstack([np.zeros(csi_complex.shape[1]), angle_diff])  # Inclui a primeira linha
    return np.abs(csi_complex) * np.exp(1j * angle_diff)

def apply_hampel_filter_to_complex(csi_complex, window_size=5):
    real_part = pd.DataFrame(csi_complex.real)
    imag_part = pd.DataFrame(csi_complex.imag)
    real_part_filtered = real_part.apply(lambda x: hampel_filter_for_series(x, window_size))
    imag_part_filtered = imag_part.apply(lambda x: hampel_filter_for_series(x, window_size))
    return real_part_filtered.values + 1j * imag_part_filtered.values

def read_csi_data_from_csv(file_path):
    df = pd.read_csv(file_path, skip_blank_lines=True)
    for i, row in df.iterrows():
        csi_str = row['data'].strip('[]')
        csi_values = np.fromstring(csi_str, sep=', ', dtype=np.float32)
        csi_complex = csi_values[::2] + 1j * csi_values[1::2]
        csi_complex_filtered = apply_hampel_filter_to_complex(csi_complex)
        csi_complex_calibrated = phase_calibration(csi_complex_filtered)
        csi_data_array[:-1] = csi_data_array[1:]
        csi_data_array[-1, :] = np.abs(csi_complex_calibrated[:CSI_DATA_COLUMNS].flatten())

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Read CSI data from a CSV file and display it graphically")
    parser.add_argument('-f', '--file', dest='file_path', action='store', required=True, help="Path to the CSV file containing CSI data")
    args = parser.parse_args()
    app = QApplication(sys.argv)
    read_csi_data_from_csv(args.file_path)
    window = CsiDataGraphicalWindow()
    window.show()
    sys.exit(app.exec_())


