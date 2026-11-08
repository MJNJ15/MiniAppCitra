import cv2
import numpy as np
from PySide6.QtCore import QThread, Signal
from PySide6.QtGui import QPixmap

from utils.image_utils import cv2_to_qpixmap


class WebcamWorker(QThread):
    """Membaca frame webcam di thread terpisah agar UI tetap responsif.

    Mengirim ke UI:
      - frame raw & histogram-nya                → panel kiri
      - frame hasil proses & histogram-nya      → panel kanan (jika ada processor aktif)
    """
    frame_raw_ready = Signal(QPixmap)
    frame_processed_ready = Signal(QPixmap)
    error_occurred = Signal(str)
    started_signal = Signal()
    stopped_signal = Signal()

    hist_raw_ready = Signal(object)
    hist_processed_ready = Signal(object)

    HIST_EMIT_INTERVAL = 3  # kirim data histogram tiap 3 frame (throttle)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._running = False
        self._capture = None
        self._active_processors = []      # [(processor, params), ...]
        self._frame_count = 0
        self._last_processed_frame = None # untuk tombol Ambil Foto

    def set_processors(self, processors: list):
        """Set rantai processor yang diterapkan berurutan per frame."""
        self._active_processors = list(processors)

    def clear_processor(self):
        """Hapus semua processor aktif (kembali ke mode raw only)."""
        self._active_processors = []

    def snapshot_processed(self):
        """Salinan frame hasil proses terbaru (None jika belum ada)."""
        if self._last_processed_frame is None:
            return None
        return self._last_processed_frame.copy()

    def run(self):
        self._capture = cv2.VideoCapture(0)

        if not self._capture.isOpened():
            self.error_occurred.emit("Gagal membuka webcam. Pastikan kamera terhubung.")
            return

        self._running = True
        self.started_signal.emit()

        while self._running:
            ret, frame = self._capture.read()
            if not ret:
                self.error_occurred.emit("Gagal membaca frame dari webcam.")
                break

            self._frame_count += 1
            emit_hist = (self._frame_count % self.HIST_EMIT_INTERVAL == 0)

            # Selalu kirim frame mentah ke panel kiri
            try:
                raw_pixmap = cv2_to_qpixmap(frame)
                self.frame_raw_ready.emit(raw_pixmap)
            except Exception:
                pass

            # Kirim data histogram (bukan gambar) agar UI tidak perlu menghitung ulang
            if emit_hist:
                try:
                    self.hist_raw_ready.emit(self._compute_histogram(frame))
                except Exception:
                    pass

            # Jika ada processor aktif, proses berantai lalu kirim ke panel kanan
            if self._active_processors:
                try:
                    processed = frame.copy()
                    for processor, params in self._active_processors:
                        processed = processor.process(processed, **params)
                    self._last_processed_frame = processed.copy()  # untuk Ambil Foto
                    processed_pixmap = cv2_to_qpixmap(processed)
                    self.frame_processed_ready.emit(processed_pixmap)
                    if emit_hist:
                        self.hist_processed_ready.emit(self._compute_histogram(processed))
                except Exception:
                    # Jika proses gagal, jangan tampilkan apa-apa di panel kanan
                    pass

        if self._capture is not None:
            self._capture.release()
        self.stopped_signal.emit()

    @staticmethod
    def _compute_histogram(image: np.ndarray) -> np.ndarray:
        """
        Menghitung histogram per-channel secara efisien (murah, <1 ms).
        Hasil: (256, 3) untuk citra berwarna, (256,) untuk grayscale.
        """
        if len(image.shape) == 3:
            hists = [
                cv2.calcHist([image], [i], None, [256], [0, 256]).ravel()
                for i in range(3)
            ]
            return np.stack(hists, axis=1)
        return cv2.calcHist([image], [0], None, [256], [0, 256]).ravel()

    def stop(self):
        self._running = False
        self.wait()