import sys
import os
import cv2
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QFileDialog, QMessageBox, QToolBar
)
from PySide6.QtCore import Qt, QTimer

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.image_utils import cv2_to_qpixmap
from utils.constants import ImageConstants, UIConstants
from utils.webcam_worker import WebcamWorker
from ui.image_panel import ImagePanel
from ui.method_panel import MethodPanel
from ui.control_panel import ControlPanel

from processors import (
    ThresholdingProcessor, DoubleThresholdingProcessor, GrayscaleProcessor,
    NegativeProcessor, BrightnessProcessor, ContrastProcessor,
    NoiseProcessor, EdgeDetectionProcessor, EqualizationProcessor,
    EmbossProcessor, SharpeningProcessor, SmoothingProcessor, ConvolutionProcessor,
    MirroringProcessor, RotationProcessor
)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.original_image_np = None
        self.result_image_np = None
        
        self.processors = {
            "Thresholding": ThresholdingProcessor(),
            "Thresholding Double": DoubleThresholdingProcessor(),
            "Grayscale": GrayscaleProcessor(),
            "Negative": NegativeProcessor(),
            "Brightness": BrightnessProcessor(),
            "Contrast": ContrastProcessor(),
            "Noise": NoiseProcessor(),
            "Edge Detection": EdgeDetectionProcessor(),
            "Equalization": EqualizationProcessor(),
            "Emboss": EmbossProcessor(),
            "Sharpening": SharpeningProcessor(),
            "Smoothing": SmoothingProcessor(),
            "Convolution": ConvolutionProcessor(),
            "Mirroring": MirroringProcessor(),
            "Rotation": RotationProcessor(),
        }
        
        # Variabel Webcam
        self.webcam_worker = None
        self.webcam_active = False

        # State histogram real-time (di-throttle via QTimer)
        self._hist_timer = None
        self._hist_raw_latest = None
        self._hist_raw_dirty = False
        self._hist_processed_latest = None
        self._hist_processed_dirty = False
        self._hist_processing_active = False
        self._right_hist_shown = False
        
        self._init_ui()
        self._create_toolbar()
        self._connect_signals()
        
        self.setWindowTitle(UIConstants.WINDOW_TITLE)
        self.resize(UIConstants.DEFAULT_WINDOW_WIDTH, UIConstants.DEFAULT_WINDOW_HEIGHT)
        self.statusBar().showMessage("Siap. Silakan buka citra atau aktifkan webcam melalui Toolbar.")

    def _init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        
        image_layout = QHBoxLayout()
        self.left_panel = ImagePanel("Citra Asli / Webcam Raw")
        self.right_panel = ImagePanel("Citra Hasil")
        image_layout.addWidget(self.left_panel)
        image_layout.addWidget(self.right_panel)
        
        control_layout = QHBoxLayout()
        self.method_panel = MethodPanel()
        self.control_panel = ControlPanel()
        
        control_layout.addWidget(self.method_panel, stretch=1)
        control_layout.addWidget(self.control_panel, stretch=1)
        
        main_layout.addLayout(image_layout, stretch=2)
        main_layout.addLayout(control_layout, stretch=1)

    def _connect_signals(self):
        self.method_panel.methods_changed.connect(self.control_panel.update_methods)
        self.method_panel.limit_exceeded.connect(
            lambda: self.statusBar().showMessage("Maksimal 5 metode dapat dipilih."))
        self.control_panel.process_requested.connect(self._on_process_requested)
        self.control_panel.webcam_toggle_requested.connect(self._on_webcam_toggle)
        self.control_panel.reset_requested.connect(self._on_reset_requested)
        self.control_panel.snapshot_requested.connect(self._on_snapshot_requested)

    def _create_toolbar(self):
        toolbar = QToolBar("Main Toolbar")
        self.addToolBar(toolbar)
        toolbar.addAction("📂 Buka", self.open_image)
        toolbar.addAction("💾 Simpan", self.save_image)

    # =================================================================
    # LOGIKA WEBCAM (ALUR BARU)
    # =================================================================
    
    def _on_webcam_toggle(self):
        """Toggle webcam: mulai atau hentikan."""
        if not self.webcam_active:
            self._start_webcam()
        else:
            self._stop_webcam()

    def _start_webcam(self):
        """
        Memulai webcam TANPA perlu memilih metode.
        Panel kiri menampilkan feed mentah, panel kanan dikosongkan.
        """
        self.method_panel.clear_selection()
        self.control_panel.clear_inputs()
        self.webcam_worker = WebcamWorker()
        
        # Hubungkan sinyal
        self.webcam_worker.frame_raw_ready.connect(self._on_webcam_frame_raw_ready)
        self.webcam_worker.frame_processed_ready.connect(self._on_webcam_frame_processed_ready)
        self.webcam_worker.error_occurred.connect(self._on_webcam_error)
        self.webcam_worker.started_signal.connect(self._on_webcam_started)
        self.webcam_worker.stopped_signal.connect(self._on_webcam_stopped)
        self.webcam_worker.hist_raw_ready.connect(self._on_webcam_hist_raw_ready)
        self.webcam_worker.hist_processed_ready.connect(self._on_webcam_hist_processed_ready)

        # Timer throttle: histogram dirender maksimal ~8x/detik, bukan tiap frame
        self._hist_timer = QTimer(self)
        self._hist_timer.setInterval(120)
        self._hist_timer.timeout.connect(self._flush_hist_updates)
        self._hist_timer.start()

        self.webcam_worker.start()
        self.statusBar().showMessage("Memulai webcam...")

    def _stop_webcam(self):
        """Menghentikan webcam dan membersihkan semua panel."""
        if self.webcam_worker:
            self.webcam_worker.stop()
            self.webcam_worker = None

    def _on_webcam_frame_raw_ready(self, pixmap):
        """Terima frame mentah dari webcam → tampilkan di panel KIRI."""
        self.left_panel.set_image(pixmap, smooth=False)

    def _on_webcam_frame_processed_ready(self, pixmap):
        """Terima frame hasil proses → tampilkan di panel KANAN."""
        self.right_panel.set_image(pixmap, smooth=False)

    def _on_webcam_hist_raw_ready(self, hist):
        """Terima data histogram frame mentah (tidak langsung render, menunggu timer)."""
        self._hist_raw_latest = hist
        self._hist_raw_dirty = True

    def _on_webcam_hist_processed_ready(self, hist):
        """Terima data histogram frame hasil proses (tidak langsung render, menunggu timer)."""
        self._hist_processed_latest = hist
        self._hist_processed_dirty = True

    def _flush_hist_updates(self):
        """Render histogram tertunda secara terkumpul (throttle 120ms)."""
        if self._hist_raw_dirty:
            self.left_panel.update_histogram_counts(self._hist_raw_latest)
            self._hist_raw_dirty = False

        if self._hist_processed_dirty:
            self.right_panel.update_histogram_counts(self._hist_processed_latest)
            self._hist_processed_dirty = False
            self._right_hist_shown = True
        elif self.webcam_active and not self._hist_processing_active and self._right_hist_shown:
            # Tidak ada processor aktif → bersihkan histogram panel kanan
            self.right_panel.histogram_widget.clear()
            self._right_hist_shown = False

    def _on_webcam_error(self, message: str):
        QMessageBox.critical(self, "Error Webcam", message)
        self._stop_webcam()

    def _on_webcam_started(self):
        self.webcam_active = True
        self.control_panel.set_webcam_state(True)
        self.right_panel.clear()  # Panel kanan kosong sampai user klik Proses
        self.statusBar().showMessage("Webcam aktif. Pilih metode lalu klik 'Proses' untuk melihat hasil di panel kanan.")

    def _on_webcam_stopped(self):
        self.webcam_active = False
        self.control_panel.set_webcam_state(False)
        self.original_image_np = None
        self.result_image_np = None
        self.left_panel.clear()
        self.right_panel.clear()

        # Bersihkan timer & state histogram real-time
        if self._hist_timer is not None:
            self._hist_timer.stop()
            self._hist_timer = None
        self._hist_raw_latest = None
        self._hist_raw_dirty = False
        self._hist_processed_latest = None
        self._hist_processed_dirty = False
        self._hist_processing_active = False
        self._right_hist_shown = False

        self.statusBar().showMessage("Webcam dihentikan.")

    def _on_snapshot_requested(self):
        """Tombol 'Ambil Foto': tangkap frame mentah terbaru ke panel kiri."""
        if not self.webcam_active or self.webcam_worker is None:
            return

        frame = self.webcam_worker.snapshot_raw()
        if frame is None:
            QMessageBox.warning(self, "Peringatan", "Belum ada frame dari webcam.")
            return

        self.original_image_np = frame.copy()
        self.result_image_np = frame.copy()  # agar tombol Simpan berfungsi

        pixmap = cv2_to_qpixmap(frame)
        self.left_panel.set_image(pixmap, smooth=True)
        self.left_panel.update_histogram(frame)

        h, w = frame.shape[:2]
        self.statusBar().showMessage(f"Foto diambil: {w}x{h} px. Klik 💾 Simpan untuk menyimpan.")

    # =================================================================
    # LOGIKA TOMBOL PROSES (CERDAS: Statis vs Webcam)
    # =================================================================
    
    def _on_process_requested(self, params_list: list):
        """
        Handler tombol Proses.
        params_list: [(nama_metode + parameter), ...] sesuai urutan proses.
        """
        if not params_list:
            return

        # Validasi semua metode dikenal
        for item in params_list:
            method_name = item.get("method")
            if method_name not in self.processors:
                QMessageBox.critical(self, "Error",
                                     f"Processor untuk '{method_name}' tidak ditemukan.")
                return

        if self.webcam_active:
            # MODE WEBCAM: daftar processor diterapkan berantai di worker
            chain = [
                (self.processors[item["method"]],
                 {k: v for k, v in item.items() if k != "method"})
                for item in params_list
            ]
            self.webcam_worker.set_processors(chain)
            self._hist_processing_active = True
            names = " → ".join(item["method"] for item in params_list)
            self.statusBar().showMessage(f"Webcam: rantai [{names}] aktif secara real-time.")
        else:
            # MODE STATIS: proses citra dengan seluruh rantai
            self._process_static_image(params_list)

    def _process_static_image(self, params_list: list):
        """Memproses citra statis melalui seluruh rantai metode."""
        if self.original_image_np is None:
            QMessageBox.warning(self, "Peringatan",
                                "Muat citra terlebih dahulu melalui tombol '📂 Buka', atau aktifkan webcam.")
            return

        try:
            names = " → ".join(item["method"] for item in params_list)
            self.statusBar().showMessage(f"Memproses: {names}...")

            result = self.original_image_np.copy()
            for item in params_list:
                processor = self.processors[item["method"]]
                kwargs = {k: v for k, v in item.items() if k != "method"}
                result = processor.process(result, **kwargs)
            self.result_image_np = result

            pixmap = cv2_to_qpixmap(result)
            self.right_panel.set_image(pixmap)
            self.right_panel.update_histogram(result)
            self.statusBar().showMessage(f"Selesai memproses: {names}")
        except Exception as e:
            self.statusBar().showMessage("Terjadi error saat memproses.")
            QMessageBox.critical(self, "Error", f"Gagal memproses citra:\n{str(e)}")

    # =================================================================
    # LOGIKA TOMBOL RESET
    # =================================================================

    def _on_reset_requested(self):
        """
        Handler saat tombol Reset diklik.
        Melakukan cleanup lengkap: deselect metode, kosongkan input, kosongkan hasil.
        """
        # 1. Deselect semua radio button di MethodPanel
        self.method_panel.clear_selection()
        
        # 2. Kosongkan panel input nilai
        self.control_panel.clear_inputs()

        if self.webcam_active:
            # --- MODE WEBCAM ---
            # Hapus processor aktif dari worker agar hanya menampilkan feed mentah
            if self.webcam_worker:
                self.webcam_worker.clear_processor()

            # Reset state histogram hasil proses
            self._hist_processing_active = False
            self._hist_processed_dirty = False
            self._hist_processed_latest = None
            self._right_hist_shown = False
            self.right_panel.histogram_widget.clear()
            
            # Kosongkan HANYA panel kanan (hasil proses)
            self.right_panel.clear()
            self.result_image_np = None
            
            self.statusBar().showMessage("Reset metode berhasil. Webcam tetap aktif (mode raw).")
            
        else:
            # --- MODE GAMBAR STATIS ---
            # Hapus data gambar dari memori
            self.original_image_np = None
            self.result_image_np = None
            
            # Kosongkan KEDUA panel (kiri dan kanan)
            self.left_panel.clear()
            self.right_panel.clear()
            
            self.statusBar().showMessage("Reset berhasil. Semua metode dan hasil telah dihapus.")

    # =================================================================
    # MANAJEMEN FILE
    # =================================================================
    
    def open_image(self):
        """Membuka citra dari file. Otomatis menghentikan webcam jika aktif."""
        if self.webcam_active:
            self._stop_webcam()

        self.method_panel.clear_selection()
        self.control_panel.clear_inputs()
            
        file_path, _ = QFileDialog.getOpenFileName(self, "Buka Citra", "", ImageConstants.SUPPORTED_FORMATS)
        if file_path:
            self.original_image_np = cv2.imread(file_path)
            if self.original_image_np is not None:
                pixmap = cv2_to_qpixmap(self.original_image_np)
                self.left_panel.set_image(pixmap)
                self.left_panel.update_histogram(self.original_image_np)
                
                h, w, ch = self.original_image_np.shape
                self.statusBar().showMessage(f"Citra dimuat: {os.path.basename(file_path)} | {w}x{h} px | {ch} channel")
                
                self.result_image_np = None
                self.right_panel.clear()
            else:
                QMessageBox.critical(self, "Error", "Gagal memuat citra.")

    def save_image(self):
        """Menyimpan citra hasil (dari proses statis atau screenshot dari webcam)."""
        # Untuk webcam, kita bisa mengambil frame terakhir dari panel kanan
        # Tapi untuk kesederhanaan, kita hanya simpan dari citra statis
        if self.result_image_np is None:
            QMessageBox.warning(self, "Peringatan", "Tidak ada citra hasil untuk disimpan.")
            return
            
        file_path, _ = QFileDialog.getSaveFileName(self, "Simpan Citra Hasil", "", "PNG (*.png);;JPEG (*.jpg *.jpeg);;BMP (*.bmp)")
        if file_path:
            success = cv2.imwrite(file_path, self.result_image_np)
            if success:
                self.statusBar().showMessage(f"Citra disimpan ke: {file_path}")
                QMessageBox.information(self, "Sukses", "Citra berhasil disimpan.")
            else:
                QMessageBox.critical(self, "Error", "Gagal menyimpan citra.")

    def closeEvent(self, event):
        """Pastikan webcam dihentikan saat aplikasi ditutup."""
        if self.webcam_active:
            self._stop_webcam()
        event.accept()