import matplotlib
# Memaksa Matplotlib menggunakan backend Qt untuk PySide6
matplotlib.use('QtAgg') 

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PySide6.QtWidgets import QWidget, QVBoxLayout
import numpy as np

class HistogramWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Inisialisasi Figure dan Canvas Matplotlib
        self.figure = Figure(figsize=(4, 2.5), dpi=100, tight_layout=True)
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)
        
        # Styling dasar untuk histogram
        self.ax.set_facecolor('#f0f0f0')
        self.ax.tick_params(axis='both', which='major', labelsize=6)
        
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

    def update_histogram(self, image_np: np.ndarray):
        """Memperbarui grafik histogram berdasarkan array NumPy citra."""
        self.ax.clear()
        
        if image_np is None or image_np.size == 0:
            self.canvas.draw()
            return

        # Cek apakah citra berwarna (3 channel) atau grayscale (2 channel)
        if len(image_np.shape) == 3:
            colors = ('r', 'g', 'b')
            for i, color in enumerate(colors):
                self.ax.hist(image_np[:,:,i].ravel(), 256, [0, 256], color=color, alpha=0.6, lw=0.5)
        else:
            self.ax.hist(image_np.ravel(), 256, [0, 256], color='black', alpha=0.7)
            
        self.ax.set_xlim([0, 256])
        self.canvas.draw()

    def clear(self):
        """Membersihkan grafik histogram."""
        self.ax.clear()
        self.canvas.draw()