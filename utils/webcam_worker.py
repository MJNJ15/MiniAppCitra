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

    def __init__(self, parent=None):
        super().__init__(parent)
        self._running = False
        self._capture = None
        self._active_processor = None
        self._current_params = {}

    def set_processor(self, processor: BaseProcessor, params: dict = None):
        """
        Mengganti processor DAN parameter secara dinamis.
        params: dict berisi parameter dari UI (misal: {'threshold': 50})
        """
        self._active_processor = processor
        if params is not None:
            self._current_params = {k: v for k, v in params.items() if k != 'method'}

    def clear_processor(self):
        """Menghapus processor aktif (kembali ke mode raw only)."""
        self._active_processor = None

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

            # Selalu kirim frame mentah ke panel kiri
            try:
                raw_pixmap = cv2_to_qpixmap(frame)
                self.frame_raw_ready.emit(raw_pixmap)
            except Exception:
                pass

            # Jika ada processor aktif, proses dan kirim ke panel kanan
            if self._active_processor is not None:
                try:
                    processed = self._active_processor.process(frame.copy(), **self._current_params)
                    processed_pixmap = cv2_to_qpixmap(processed)
                    self.frame_processed_ready.emit(processed_pixmap)
                except Exception:
                    # Jika proses gagal, jangan tampilkan apa-apa di panel kanan
                    pass

        if self._capture is not None:
            self._capture.release()
        self.stopped_signal.emit()

    def stop(self):
        self._running = False
        self.wait()