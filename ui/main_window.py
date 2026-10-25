import sys
import os
import cv2
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QFileDialog, QMessageBox, QToolBar
)
from PySide6.QtCore import Qt

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
        self.method_panel.method_selected.connect(self.control_panel.update_inputs)
        self.method_panel.method_cleared.connect(self._on_method_cleared)
        self.control_panel.process_requested.connect(self._on_process_requested)
        self.control_panel.webcam_toggle_requested.connect(self._on_webcam_toggle)
        self.control_panel.reset_requested.connect(self._on_reset_requested)

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
        
        self.webcam_worker.start()
        self.statusBar().showMessage("Memulai webcam...")

    def _stop_webcam(self):
        """Menghentikan webcam dan membersihkan semua panel."""
        if self.webcam_worker:
            self.webcam_worker.stop()
            self.webcam_worker = None

    def _on_webcam_frame_raw_ready(self, pixmap):
        """Terima frame mentah dari webcam → tampilkan di panel KIRI."""
        self.left_panel.set_image(pixmap)

    def _on_webcam_frame_processed_ready(self, pixmap):
        """Terima frame hasil proses → tampilkan di panel KANAN."""
        self.right_panel.set_image(pixmap)

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
        self.statusBar().showMessage("Webcam dihentikan.")

    # =================================================================
    # LOGIKA TOMBOL PROSES (CERDAS: Statis vs Webcam)
    # =================================================================
    
    def _on_process_requested(self, params: dict):
        """
        Handler tombol Proses. Berperilaku berbeda tergantung mode:
        - Jika webcam AKTIF: terapkan metode ke webcam secara real-time (panel kanan)
        - Jika webcam TIDAK AKTIF: proses citra statis yang dimuat
        """
        method_name = params.get('method')
        processor = self.processors.get(method_name)
        
        if not processor:
            QMessageBox.critical(self, "Error", f"Processor untuk '{method_name}' tidak ditemukan.")
            return
        
        if self.webcam_active:
            # MODE WEBCAM: terapkan processor ke worker yang sedang berjalan
            self.webcam_worker.set_processor(processor, params)
            self.statusBar().showMessage(f"Webcam: metode '{method_name}' diterapkan secara real-time  {params}.")
        else:
            # MODE STATIS: proses citra yang dimuat dari file
            self._process_static_image(processor, params)

    def _process_static_image(self, processor, params: dict):
        """Memproses citra statis yang dimuat dari file."""
        if self.original_image_np is None:
            QMessageBox.warning(self, "Peringatan", 
                                "Muat citra terlebih dahulu melalui tombol '📂 Buka', atau aktifkan webcam.")
            return
        
        try:
            self.statusBar().showMessage(f"Memproses: {params.get('method')}...")
            self.result_image_np = processor.process(self.original_image_np, **params)
            
            pixmap = cv2_to_qpixmap(self.result_image_np)
            self.right_panel.set_image(pixmap)
            self.right_panel.update_histogram(self.result_image_np)
            self.statusBar().showMessage(f"Selesai memproses: {params.get('method')}")
        except Exception as e:
            self.statusBar().showMessage("Terjadi error saat memproses.")
            QMessageBox.critical(self, "Error", f"Gagal memproses citra:\n{str(e)}")

    # =================================================================
    # LOGIKA TOMBOL RESET
    # =================================================================

    def _on_method_cleared(self):
        """Handler saat pemilihan metode di-clear dari MethodPanel."""
        self.control_panel.clear_inputs()

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