from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter, QColor, QFont
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

    @staticmethod
    def _nice(v):
        """Bulatkan ke angka 'nice' (1/2/5 * 10^n)."""
        if v <= 0:
            return 0
        exp = int(np.floor(np.log10(v)))
        base = 10 ** exp
        for m in (1, 2, 5, 10):
            if v <= m * base:
                return int(m * base)
        return int(base * 10)

    @staticmethod
    def _fmt_count(v):
        """Format jumlah piksel ringkas: 150000 -> '150k'."""
        if v >= 1000:
            return f"{v / 1000:.0f}k"
        return str(int(v))

    def paintEvent(self, event):
        p = QPainter(self)
        w, h = self.width(), self.height()

        # Margin untuk label sumbu
        mL, mR, mT, mB = 44, 6, 4, 16
        pw = max(10, w - mL - mR)
        ph = max(10, h - mT - mB)
        x0, y0 = mL, mT

        c = self._counts
        if c is None:
            p.setPen(QColor(120, 120, 120))
            p.drawRect(x0, y0, pw, ph)
            p.end()
            return

        raw = c.astype(np.float64)
        n_channels = raw.shape[1] if raw.ndim == 2 else 1

        # Histogram biner/tepi sangat jarang — gunakan skala log10 agar
        # lonjakan tetap terlihat.
        sparse = float((raw > 0).mean()) < 0.1
        transform = (lambda v: np.log10(1.0 + v)) if sparse else (lambda v: v)
        data = transform(raw)
        dmax = float(data.max()) if data.size else 1.0
        if dmax <= 0:
            dmax = 1.0

        def y_for(count):
            d = float(transform(np.array([count]))[0])
            return y0 + ph - (d / dmax) * ph

        if n_channels == 3:
            colors = self.CHANNEL_COLORS
            heights = data.transpose()  # (3, 256)
        else:
            colors = (self.GRAY_COLOR,)
            heights = data.reshape(1, -1)

        # Batang histogram
        bar_w = max(1, int(pw / 256))
        for ch in range(n_channels):
            p.setPen(colors[ch])
            p.setBrush(colors[ch])
            row = heights[ch]
            for x in range(256):
                px = x0 + int(x * pw / 256)
                val = float(row[x]) / dmax * ph
                y = int(y0 + ph - val)
                if y < y0 + ph:
                    p.drawRect(px, y, bar_w, y0 + ph - y)

        # Bingkai + garis dasar
        p.setPen(QColor(120, 120, 120))
        p.drawRect(x0, y0, pw, ph)
        p.setFont(QFont("Arial", 7))

        # Sumbu X: nilai piksel (0, 64, 128, 192, 255)
        for v in (0, 64, 128, 192, 255):
            px = x0 + int(v * pw / 256)
            p.drawLine(px, y0 + ph, px, y0 + ph + 3)
            label = str(v)
            tw = p.fontMetrics().horizontalAdvance(label)
            p.drawText(int(px - tw / 2), y0 + ph + 12, label)

        # Sumbu Y: jumlah piksel (0, setengah max, max — angka nice)
        ticks = sorted(set([0, self._nice(raw.max() / 2), self._nice(raw.max())]))
        for t in ticks:
            ty = int(min(max(y_for(t), y0), y0 + ph))
            p.drawLine(x0 - 3, ty, x0, ty)
            p.drawText(4, max(ty, y0 + 7) + 3, self._fmt_count(t))

        p.end()
