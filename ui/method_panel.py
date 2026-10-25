from PySide6.QtWidgets import QWidget, QVBoxLayout, QGridLayout, QRadioButton, QGroupBox
from PySide6.QtCore import Signal

class MethodPanel(QWidget):
    # Sinyal dikirim saat metode berubah: (nama_metode, parameter_default)
    method_selected = Signal(str, dict)
    method_cleared = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.radio_buttons = {}
        self._init_ui()

    def _init_ui(self):
        group = QGroupBox("METODE")
        layout = QGridLayout()
        
        # Daftar metode sesuai planner.md
        methods = [
            ("Thresholding", {"threshold": 128}),
            ("Thresholding Double", {"t1": 50, "t2": 150}),
            ("Grayscale", {}),
            ("Negative", {}),
            ("Brightness", {"value": 0}),
            ("Contrast", {"factor": 1.0}),
            # Placeholder untuk M3 & M4
            ("Noise", {}),
            ("Edge Detection", {}),
            ("Equalization", {}),
            ("Emboss", {}),
            ("Sharpening", {}),
            ("Smoothing", {}),
            ("Convolution", {}),
            ("Mirroring", {}),
            ("Rotation", {}),
        ]
        
        row, col = 0, 0
        for name, params in methods:
            rb = QRadioButton(name)
            rb.method_name = name
            rb.default_params = params
            rb.toggled.connect(self._on_method_toggled)
            self.radio_buttons[name] = rb
            layout.addWidget(rb, row, col)
            col += 1
            if col == 3:  # 3 kolom sesuai spesifikasi layout
                col = 0
                row += 1
                
        group.setLayout(layout)
        main_layout = QVBoxLayout()
        main_layout.addWidget(group)
        self.setLayout(main_layout)

    def _on_method_toggled(self, checked: bool):
        if checked:
            rb = self.sender()
            self.method_selected.emit(rb.method_name, rb.default_params)

    def clear_selection(self):
        """Menghilangkan semua pilihan radio button."""
        # Block sinyal sementara agar tidak trigger method_selected
        for rb in self.radio_buttons.values():
            # 1. Block sinyal agar tidak memicu method_selected saat di-uncheck
            rb.blockSignals(True)
            
            # 2. Matikan sifat eksklusif (KUNCI PERBAIKAN)
            # Ini mengizinkan state di mana TIDAK ADA radio button yang terpilih
            rb.setAutoExclusive(False)
            
            # 3. Uncheck radio button
            rb.setChecked(False)
            
            # 4. Kembalikan sifat eksklusif agar kembali berfungsi seperti radio button normal
            rb.setAutoExclusive(True)
            
            # 5. Buka block sinyal
            rb.blockSignals(False)
        
        # Emit sinyal bahwa selection telah di-clear
        self.method_cleared.emit()