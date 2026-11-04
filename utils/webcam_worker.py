import cv2
import numpy as np
from PySide6.QtCore import QThread, Signal
from PySide6.QtGui import QPixmap

from utils.image_utils import cv2_to_qpixmap
from processors.base_processor import BaseProcessor


class WebcamWorker(QThread):
    """
    QThread untuk membaca frame webcam secara real-time.
    Mengirim dua jenis sinyal:
      - frame_raw_ready: frame mentah dari kamera (untuk panel kiri)
      - frame_processed_ready: frame hasil pengolahan (untuk panel kanan, hanya jika ada processor aktif)
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
        self._active_processors = []   # [(processor, params_dict), ...]
        self._frame_count = 0

    def set_processors(self, processors: list):
        """
        Mengatur rantai processor yang diterapkan berurutan per frame.
        processors: [(BaseProcessor, dict_parameter), ...] sesuai urutan.
        """
        self._active_processors = list(processors)

    def set_processor(self, processor: BaseProcessor, params: dict = None):
        """Kompatibilitas: set satu processor saja."""
        self.set_processors([(processor, params)])

    def clear_processor(self):
        """Menghapus semua processor aktif (kembali ke mode raw only)."""
        self._active_processors = []

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