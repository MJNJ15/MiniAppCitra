from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter, QColor
import numpy as np


class HistogramWidget(QWidget):
    """
    Widget histogram berbasis QPainter murni (tanpa Matplotlib).

    Mengapa: pengukuran (640x480, offscreen) menunjukkan Matplotlib
    canvas.draw_idle() memakan ~140 ms per update — tidak layak untuk
    mode webcam real-time. QPainter menghabiskan <0,1 ms, sehingga
    jalur histogram tidak lagi menjadi bottleneck UI thread.

    API tetap kompatibel:
      - update_histogram(image_np)      : terima array citra
      - update_histogram_counts(counts) : terima data histogram siap pakai
      - clear()                         : kosongkan grafik
    """

    BG_COLOR = QColor("#f0f0f0")
    CHANNEL_COLORS = (
        QColor(255, 0, 0, 160),
        QColor(0, 170, 0, 160),
        QColor(0, 0, 255, 160),
    )
    GRAY_COLOR = QColor(40, 40, 40, 190)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._counts = None  # (256,) untuk grayscale, (256,3) untuk warna
        self.setMinimumHeight(80)

    def update_histogram(self, image_np: np.ndarray):
        """API lama: menerima array citra, menghitung histogram lalu render."""
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

        self._counts = np.asarray(counts)
        self.update()  # trigger paintEvent (murah)

    def clear(self):
        """Membersihkan grafik histogram."""
        self._counts = None
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        w, h = self.width(), self.height()
        p.fillRect(self.rect(), self.BG_COLOR)

        c = self._counts
        if c is None:
            p.end()
            return

        n_channels = c.shape[1] if c.ndim == 2 else 1
        ymax = float(c.max()) if c.size else 1.0
        if ymax <= 0:
            ymax = 1.0
        scale = (h - 4) / ymax

        if n_channels == 3:
            colors = self.CHANNEL_COLORS
            heights = c.transpose()  # (3, 256)
        else:
            colors = (self.GRAY_COLOR,)
            heights = c.reshape(1, -1)

        # Garis dasar sumbu
        p.setPen(QColor(120, 120, 120))
        p.drawLine(0, h - 2, w, h - 2)

        for ch in range(n_channels):
            p.setPen(colors[ch])
            row = heights[ch]
            for x in range(256):
                px = int(x * w / 256)
                val = float(row[x]) * scale
                p.drawLine(px, h - 2, px, int(h - 2 - val))

        p.end()
