import matplotlib
# Memaksa Matplotlib menggunakan backend Qt untuk PySide6
matplotlib.use('QtAgg') 

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PySide6.QtWidgets import QWidget, QVBoxLayout
import numpy as np

class HistogramWidget(QWidget):
    COLORS = ('r', 'g', 'b')

    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Inisialisasi Figure dan Canvas Matplotlib
        self.figure = Figure(figsize=(4, 2.5), dpi=100, tight_layout=True)
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)
        
        # Styling dasar untuk histogram
        self.ax.set_facecolor('#f0f0f0')
        self.ax.tick_params(axis='both', which='major', labelsize=6)

        self._bars = []          # BarContainer per channel (dibuat sekali)
        self._n_channels = None  # jumlah channel yang sedang dirender
        
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

    def update_histogram(self, image_np: np.ndarray):
        """API lama: menerima array citra, menghitung histogram lalu render cepat."""
        if image_np is None or image_np.size == 0:
            self.clear()
            return

        if len(image_np.shape) == 3:
            counts = np.stack(
                [np.histogram(image_np[:, :, i], 256, (0, 256))[0] for i in range(3)],
                axis=1,
            )
        else:
            counts = np.histogram(image_np.ravel(), 256, (0, 256))[0]

        self.update_histogram_counts(counts)

    def update_histogram_counts(self, counts: np.ndarray):
        """
        Terima hasil hitung histogram langsung (mis. dari worker webcam).
        counts: (256, 3) untuk berwarna, (256,) untuk grayscale.
        """
        if counts is None or counts.size == 0:
            self.clear()
            return

        n_channels = counts.shape[1] if counts.ndim == 2 else 1
        if self._n_channels != n_channels:
            self._build_bars(n_channels)

        # Update tinggi bar in-place (tidak membuat artist baru)
        for i, bars in enumerate(self._bars):
            heights = counts[:, i] if counts.ndim == 2 else counts
            for rect, h in zip(bars.patches, heights):
                rect.set_height(float(h))

        # Autoscale sumbu Y saja agar puncak selalu proporsional dan terlihat
        self.ax.relim()
        self.ax.autoscale_view(scaley=True, scalex=False)
        self.canvas.draw_idle()

    def _build_bars(self, n_channels: int):
        """Membuat bar sekali untuk jumlah channel tertentu."""
        self.ax.clear()
        self._bars = []
        self._n_channels = n_channels

        self.ax.set_facecolor('#f0f0f0')
        self.ax.tick_params(axis='both', which='major', labelsize=6)
        self.ax.set_xlim([0, 256])

        x = np.arange(256)
        for i in range(n_channels):
            color = self.COLORS[i] if n_channels == 3 else 'black'
            bars = self.ax.bar(x, np.zeros(256), color=color, alpha=0.6, width=1.0)
            self._bars.append(bars)

    def clear(self):
        """Membersihkan grafik histogram."""
        self.ax.clear()
        self._bars = []
        self._n_channels = None
        self.canvas.draw_idle()