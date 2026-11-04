from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QGroupBox, QHBoxLayout, QScrollArea,
    QPushButton, QLabel, QSpinBox, QDoubleSpinBox,
    QSlider, QComboBox, QGridLayout,
)
from PySide6.QtCore import Signal, Qt


class ControlPanel(QWidget):
    process_requested = Signal(object)
    webcam_toggle_requested = Signal()
    reset_requested = Signal()
    snapshot_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.method_groups = []   # [{'name', 'widgets', 'kernel'}, ...]
        self.webcam_active = False
        self._init_ui()

    def _init_ui(self):
        main_layout = QVBoxLayout()
        
        process_group = QGroupBox("PROSES")
        process_layout = QHBoxLayout()
        
        self.btn_process = QPushButton("▶ Proses")
        self.btn_process.setStyleSheet("font-weight: bold; font-size: 14px; min-height: 30px; background-color: #2196F3; color: white;")
        self.btn_process.clicked.connect(self._on_process_clicked)
        process_layout.addWidget(self.btn_process)
        
        self.btn_webcam = QPushButton("📷 Webcam")
        self.btn_webcam.setStyleSheet("font-weight: bold; font-size: 14px; min-height: 30px; background-color: #4CAF50; color: white;")
        self.btn_webcam.clicked.connect(self._on_webcam_toggle)
        process_layout.addWidget(self.btn_webcam)

        self.btn_snapshot = QPushButton("Ambil Foto")
        self.btn_snapshot.setStyleSheet("font-weight: bold; font-size: 14px; min-height: 30px; background-color: #607D8B; color: white;")
        self.btn_snapshot.setVisible(False)  # muncul hanya saat webcam menyala
        self.btn_snapshot.clicked.connect(self._on_snapshot_clicked)
        process_layout.addWidget(self.btn_snapshot)

        self.btn_reset = QPushButton("🔄 Reset")
        self.btn_reset.setStyleSheet("font-weight: bold; font-size: 14px; min-height: 30px; background-color: #FF9800; color: white;")
        self.btn_reset.clicked.connect(self._on_reset_clicked)
        process_layout.addWidget(self.btn_reset)
        
        process_group.setLayout(process_layout)
        
        # Area input di dalam scroll area agar muat untuk banyak metode
        self.input_group = QGroupBox("INPUT NILAI")
        self.input_scroll = QScrollArea()
        self.input_scroll.setWidgetResizable(True)
        self.input_content = QWidget()
        self.input_layout = QVBoxLayout(self.input_content)
        self.input_scroll.setWidget(self.input_content)

        outer_layout = QVBoxLayout()
        outer_layout.addWidget(self.input_scroll)
        self.input_group.setLayout(outer_layout)

        main_layout.addWidget(process_group)
        main_layout.addWidget(self.input_group)
        self.setLayout(main_layout)

    def set_webcam_state(self, active: bool):
        """Update status tombol webcam. Tombol Proses TIDAK dinonaktifkan."""
        self.webcam_active = active
        self.btn_snapshot.setVisible(active)
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

    def _on_snapshot_clicked(self):
        """Handler tombol 'Ambil Foto' — hanya bermakna saat webcam aktif."""
        self.snapshot_requested.emit()

    def clear_inputs(self):
        """Mengosongkan panel input nilai."""
        self._clear_layout(self.input_layout)
        self.method_groups = []

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

    def update_methods(self, methods):
        """
        Membangun panel input untuk daftar metode terpilih.
        methods: [(nama_metode, default_params), ...] sesuai urutan proses.
        """
        self._clear_layout(self.input_layout)
        self.method_groups = []

        if not methods:
            label = QLabel("Tidak ada metode yang dipilih.")
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet("color: #888; font-style: italic;")
            self.input_layout.addWidget(label)
            return

        for idx, (method_name, default_params) in enumerate(methods, start=1):
            group = QGroupBox(f"{idx}. {method_name}")
            group_layout = QVBoxLayout()
            entry = {"name": method_name, "widgets": {}, "kernel": None}
            self._build_group_inputs(group_layout, method_name, default_params, entry)
            group.setLayout(group_layout)
            self.input_layout.addWidget(group)
            self.method_groups.append(entry)

    def _build_group_inputs(self, layout, method_name, default_params, entry):
        """Bangun widget input untuk SATU metode ke dalam `layout`."""
        widgets = entry["widgets"]

        if method_name == "Thresholding":
            self._add_spinbox(layout, widgets, "threshold", "Threshold (0-255):", 0, 255, default_params.get("threshold", 128))
        elif method_name == "Thresholding Double":
            self._add_spinbox(layout, widgets, "t1", "T1 (0-255):", 0, 255, default_params.get("t1", 50))
            self._add_spinbox(layout, widgets, "t2", "T2 (0-255):", 0, 255, default_params.get("t2", 150))
        elif method_name == "Brightness":
            self._add_slider(layout, widgets, "value", "Brightness (-100 to +100):", -100, 100, default_params.get("value", 0))
        elif method_name == "Contrast":
            self._add_doublespinbox(layout, widgets, "factor", "Contrast Factor (0.5 - 3.0):", 0.5, 3.0, 0.1, default_params.get("factor", 1.0))
        elif method_name == "Noise":
            self._add_combobox(layout, widgets, "type", "Tipe Noise:", ["Gaussian", "Salt & Pepper"])
            self._add_doublespinbox(layout, widgets, "amount", "Amount (0.0 - 1.0):", 0.0, 1.0, 0.05, 0.1)
        elif method_name == "Edge Detection":
            self._add_combobox(layout, widgets, "edge_method", "Metode:", ["Canny", "Sobel X", "Sobel Y"])
        elif method_name == "Smoothing":
            self._add_combobox(layout, widgets, "type", "Tipe Blur:", ["Gaussian", "Average", "Median"])
            self._add_spinbox(layout, widgets, "kernel_size", "Kernel Size (3, 5, 7):", 3, 7, 3)
        elif method_name == "Convolution":
            layout.addWidget(QLabel("Kernel 3x3:"))
            grid_widget = QWidget()
            grid_layout = QGridLayout()
            default_kernel = [[0, 0, 0], [0, 1, 0], [0, 0, 0]]
            kernel_rows = []
            for i in range(3):
                row = []
                for j in range(3):
                    sb = QDoubleSpinBox()
                    sb.setRange(-10.0, 10.0)
                    sb.setSingleStep(0.1)
                    sb.setValue(default_kernel[i][j])
                    grid_layout.addWidget(sb, i, j)
                    row.append(sb)
                kernel_rows.append(row)
            entry["kernel"] = kernel_rows
            grid_widget.setLayout(grid_layout)
            layout.addWidget(grid_widget)
        elif method_name == "Mirroring":
            self._add_combobox(layout, widgets, "direction", "Arah Cermin:", ["Horizontal", "Vertical", "Both"])
        elif method_name == "Rotation":
            self._add_spinbox(layout, widgets, "angle", "Sudut Rotasi (0-360°):", 0, 360, default_params.get("angle", 0))
        else:
            label = QLabel("Tidak ada parameter tambahan.")
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet("color: #888; font-style: italic;")
            layout.addWidget(label)

    def _add_spinbox(self, layout, widgets, key, label_text, min_val, max_val, default):
        row = QHBoxLayout()
        row.addWidget(QLabel(label_text))
        spin = QSpinBox()
        spin.setRange(min_val, max_val)
        spin.setValue(default)
        row.addWidget(spin)
        widgets[key] = spin
        layout.addLayout(row)

    def _add_doublespinbox(self, layout, widgets, key, label_text, min_val, max_val, step, default):
        row = QHBoxLayout()
        row.addWidget(QLabel(label_text))
        spin = QDoubleSpinBox()
        spin.setRange(min_val, max_val)
        spin.setSingleStep(step)
        spin.setValue(default)
        row.addWidget(spin)
        widgets[key] = spin
        layout.addLayout(row)

    def _add_slider(self, layout, widgets, key, label_text, min_val, max_val, default):
        row = QHBoxLayout()
        row.addWidget(QLabel(label_text))
        slider = QSlider(Qt.Horizontal)
        slider.setRange(min_val, max_val)
        slider.setValue(default)
        row.addWidget(slider)
        val_label = QLabel(str(default))
        slider.valueChanged.connect(lambda v: val_label.setText(str(v)))
        row.addWidget(val_label)
        widgets[key] = slider
        layout.addLayout(row)

    def _add_combobox(self, layout, widgets, key, label_text, items):
        row = QHBoxLayout()
        row.addWidget(QLabel(label_text))
        combo = QComboBox()
        combo.addItems(items)
        row.addWidget(combo)
        widgets[key] = combo
        layout.addLayout(row)

    def _on_process_clicked(self):
        """
        Mengumpulkan parameter dari SEMUA group metode dan emit sinyal.
        Hasil: list dict, satu per metode (urut = urutan proses).
        """
        params_list = []
        for g in self.method_groups:
            params = {"method": g["name"]}
            for key, widget in g["widgets"].items():
                if isinstance(widget, (QSpinBox, QDoubleSpinBox)):
                    params[key] = widget.value()
                elif isinstance(widget, QSlider):
                    params[key] = widget.value()
                elif isinstance(widget, QComboBox):
                    params[key] = widget.currentText()
            if g["kernel"] is not None:
                params["kernel"] = [[sb.value() for sb in row] for row in g["kernel"]]
            params_list.append(params)

        self.process_requested.emit(params_list)