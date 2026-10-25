from PySide6.QtWidgets import (QWidget, QVBoxLayout, QGroupBox, QHBoxLayout, 
                               QPushButton, QLabel, QSpinBox, QDoubleSpinBox, 
                               QSlider, QComboBox, QGridLayout)
from PySide6.QtCore import Signal, Qt


class ControlPanel(QWidget):
    process_requested = Signal(dict)
    webcam_toggle_requested = Signal()
    reset_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_method = ""
        self.param_widgets = {}
        self.kernel_spinboxes = []
        self.webcam_active = False
        self._init_ui()

    def _init_ui(self):
        main_layout = QVBoxLayout()
        
        process_group = QGroupBox("PROSES")
        process_layout = QHBoxLayout()
        
        self.btn_process = QPushButton("▶ Proses")
        self.btn_process.setStyleSheet("font-weight: bold; font-size: 14px; min-height: 30px;")
        self.btn_process.clicked.connect(self._on_process_clicked)
        process_layout.addWidget(self.btn_process)
        
        self.btn_webcam = QPushButton("📷 Webcam")
        self.btn_webcam.setStyleSheet("font-weight: bold; font-size: 14px; min-height: 30px; background-color: #4CAF50; color: white;")
        self.btn_webcam.clicked.connect(self._on_webcam_toggle)
        process_layout.addWidget(self.btn_webcam)

        self.btn_reset = QPushButton("🔄 Reset")
        self.btn_reset.setStyleSheet("font-weight: bold; font-size: 14px; min-height: 30px; background-color: #FF9800; color: white;")
        self.btn_reset.clicked.connect(self._on_reset_clicked)
        process_layout.addWidget(self.btn_reset)
        
        process_group.setLayout(process_layout)
        
        self.input_group = QGroupBox("INPUT NILAI")
        self.input_layout = QVBoxLayout()
        self.input_group.setLayout(self.input_layout)
        
        main_layout.addWidget(process_group)
        main_layout.addWidget(self.input_group)
        self.setLayout(main_layout)

    def set_webcam_state(self, active: bool):
        """Update status tombol webcam. Tombol Proses TIDAK dinonaktifkan."""
        self.webcam_active = active
        if active:
            self.btn_webcam.setText("⏹ Stop Webcam")
            self.btn_webcam.setStyleSheet("font-weight: bold; font-size: 14px; min-height: 30px; background-color: #f44336; color: white;")
        else:
            self.btn_webcam.setText(" Webcam")
            self.btn_webcam.setStyleSheet("font-weight: bold; font-size: 14px; min-height: 30px; background-color: #4CAF50; color: white;")

    def _on_webcam_toggle(self):
        self.webcam_toggle_requested.emit()

    def _on_reset_clicked(self):
        """Handler saat tombol Reset diklik."""
        self.reset_requested.emit()

    def clear_inputs(self):
        """Mengosongkan panel input nilai."""
        self._clear_layout(self.input_layout)
        self.param_widgets = {}
        self.kernel_spinboxes = []
        self.current_method = ""
        
        # Tampilkan pesan informatif
        label = QLabel("Tidak ada metode yang dipilih.")
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("color: #888; font-style: italic;")
        self.input_layout.addWidget(label)

    def _clear_layout(self, layout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    self._clear_layout(item.layout())

    def update_inputs(self, method_name: str, default_params: dict):
        self.current_method = method_name
        self._clear_layout(self.input_layout)
        self.param_widgets = {}
        self.kernel_spinboxes = []

        if method_name == "Thresholding":
            self._add_spinbox("threshold", "Threshold (0-255):", 0, 255, default_params.get("threshold", 128))
        elif method_name == "Thresholding Double":
            self._add_spinbox("t1", "T1 (0-255):", 0, 255, default_params.get("t1", 50))
            self._add_spinbox("t2", "T2 (0-255):", 0, 255, default_params.get("t2", 150))
        elif method_name == "Brightness":
            self._add_slider("value", "Brightness (-100 to +100):", -100, 100, default_params.get("value", 0))
        elif method_name == "Contrast":
            self._add_doublespinbox("factor", "Contrast Factor (0.5 - 3.0):", 0.5, 3.0, 0.1, default_params.get("factor", 1.0))
        elif method_name == "Noise":
            self._add_combobox("type", "Tipe Noise:", ["Gaussian", "Salt & Pepper"])
            self._add_doublespinbox("amount", "Amount (0.0 - 1.0):", 0.0, 1.0, 0.05, 0.1)
        elif method_name == "Edge Detection":
            self._add_combobox("edge_method", "Metode:", ["Canny", "Sobel X", "Sobel Y"])
        elif method_name == "Smoothing":
            self._add_combobox("type", "Tipe Blur:", ["Gaussian", "Average", "Median"])
            self._add_spinbox("kernel_size", "Kernel Size (3, 5, 7):", 3, 7, 3)
        elif method_name == "Convolution":
            label = QLabel("Kernel 3x3:")
            self.input_layout.addWidget(label)
            grid_widget = QWidget()
            grid_layout = QGridLayout()
            default_kernel = [[0,0,0],[0,1,0],[0,0,0]]
            self.kernel_spinboxes = []
            for i in range(3):
                row = []
                for j in range(3):
                    sb = QDoubleSpinBox()
                    sb.setRange(-10.0, 10.0)
                    sb.setSingleStep(0.1)
                    sb.setValue(default_kernel[i][j])
                    grid_layout.addWidget(sb, i, j)
                    row.append(sb)
                self.kernel_spinboxes.append(row)
            grid_widget.setLayout(grid_layout)
            self.input_layout.addWidget(grid_widget)
        elif method_name == "Mirroring":
            self._add_combobox("direction", "Arah Cermin:", ["Horizontal", "Vertical", "Both"])
        elif method_name == "Rotation":
            self._add_spinbox("angle", "Sudut Rotasi (0-360°):", 0, 360, default_params.get("angle", 0))
        else:
            label = QLabel("Tidak ada parameter tambahan.")
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet("color: #888; font-style: italic;")
            self.input_layout.addWidget(label)

    def _add_spinbox(self, key, label_text, min_val, max_val, default):
        layout = QHBoxLayout()
        layout.addWidget(QLabel(label_text))
        spin = QSpinBox()
        spin.setRange(min_val, max_val)
        spin.setValue(default)
        layout.addWidget(spin)
        self.param_widgets[key] = spin
        self.input_layout.addLayout(layout)

    def _add_doublespinbox(self, key, label_text, min_val, max_val, step, default):
        layout = QHBoxLayout()
        layout.addWidget(QLabel(label_text))
        spin = QDoubleSpinBox()
        spin.setRange(min_val, max_val)
        spin.setSingleStep(step)
        spin.setValue(default)
        layout.addWidget(spin)
        self.param_widgets[key] = spin
        self.input_layout.addLayout(layout)

    def _add_slider(self, key, label_text, min_val, max_val, default):
        layout = QHBoxLayout()
        layout.addWidget(QLabel(label_text))
        slider = QSlider(Qt.Horizontal)
        slider.setRange(min_val, max_val)
        slider.setValue(default)
        layout.addWidget(slider)
        val_label = QLabel(str(default))
        slider.valueChanged.connect(lambda v: val_label.setText(str(v)))
        layout.addWidget(val_label)
        self.param_widgets[key] = slider
        self.input_layout.addLayout(layout)

    def _add_combobox(self, key, label_text, items):
        layout = QHBoxLayout()
        layout.addWidget(QLabel(label_text))
        combo = QComboBox()
        combo.addItems(items)
        layout.addWidget(combo)
        self.param_widgets[key] = combo
        self.input_layout.addLayout(layout)

    def _on_process_clicked(self):
        """
        Mengumpulkan parameter dan emit sinyal.
        MainWindow yang akan memutuskan: proses citra statis atau terapkan ke webcam.
        """
        params = {'method': self.current_method}
        for key, widget in self.param_widgets.items():
            if isinstance(widget, (QSpinBox, QDoubleSpinBox)):
                params[key] = widget.value()
            elif isinstance(widget, QSlider):
                params[key] = widget.value()
            elif isinstance(widget, QComboBox):
                params[key] = widget.currentText()
                
        if self.current_method == "Convolution" and self.kernel_spinboxes:
            kernel = [[sb.value() for sb in row] for row in self.kernel_spinboxes]
            params['kernel'] = kernel
            
        self.process_requested.emit(params)