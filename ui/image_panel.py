from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
import numpy as np
from .histogram_widget import HistogramWidget

class ImagePanel(QWidget):
    def __init__(self, title: str = "Panel Citra", parent=None):
        super().__init__(parent)
        
        self._original_pixmap = None  # Menyimpan QPixmap asli untuk di-rescale
        self._smooth_scaling = True   # True = halus (mode statis), False = cepat (webcam)

        # Setup UI
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setMinimumHeight(300)
        self.image_label.setStyleSheet("QLabel { background-color: #2b2b2b; color: #aaaaaa; border: 1px solid #555; }")
        self.image_label.setText(f"[ {title} ]\nBelum ada citra dimuat")
        
        self.histogram_widget = HistogramWidget()
        
        layout = QVBoxLayout()
        layout.addWidget(self.image_label, stretch=3)
        layout.addWidget(self.histogram_widget, stretch=1)
        layout.setContentsMargins(5, 5, 5, 5)
        self.setLayout(layout)

    def set_image(self, pixmap: QPixmap, smooth: bool = True):
        """
        Menerima QPixmap dan menampilkannya.

        Args:
            smooth: True → interpolasi halus (kualitas terbaik, cocok untuk mode statis).
                    False → scaling cepat untuk feed webcam real-time agar lebih ringan.
        """
        if pixmap.isNull():
            self.clear()
            return

        self._original_pixmap = pixmap
        self._smooth_scaling = smooth
        self._update_scaled_image()

    def _update_scaled_image(self):
        """Menyesuaikan ukuran pixmap dengan ukuran label saat ini."""
        if self._original_pixmap:
            transform = Qt.SmoothTransformation if self._smooth_scaling else Qt.FastTransformation
            scaled_pixmap = self._original_pixmap.scaled(
                self.image_label.size(),
                Qt.KeepAspectRatio,
                transform,
            )
            self.image_label.setPixmap(scaled_pixmap)

    def update_histogram(self, image_np: np.ndarray):
        """Meneruskan data array NumPy ke widget histogram."""
        self.histogram_widget.update_histogram(image_np)

    def update_histogram_counts(self, counts):
        """Meneruskan data histogram yang sudah dihitung (path webcam real-time)."""
        self.histogram_widget.update_histogram_counts(counts)

    def clear(self):
        """Merest panel ke kondisi awal."""
        self._original_pixmap = None
        self.image_label.clear()
        self.image_label.setText("Belum ada citra")
        self.histogram_widget.clear()

    def resizeEvent(self, event):
        """Override event resize untuk melakukan re-scale gambar secara dinamis."""
        super().resizeEvent(event)
        self._update_scaled_image()