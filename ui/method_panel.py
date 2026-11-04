from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QGridLayout, QCheckBox, QGroupBox,
    QHBoxLayout, QLabel, QRadioButton, QButtonGroup,
)
from PySide6.QtCore import Signal


class MethodPanel(QWidget):
    """
    Panel pemilihan metode dengan dua mode:
      - Tunggal: eksklusif (seperti radio), perilaku lama.
      - Ganda  : multi-pilih berurutan, maksimal MAX_METHODS metode.
    Urutan proses = urutan klik.
    """
    MAX_METHODS = 5

    methods_changed = Signal(object)   # [(nama, default_params), ...] sesuai urutan
    limit_exceeded = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.radio_buttons = {}      # nama -> QCheckBox
        self.mode_multi = False
        self._selected_order = []
        self._init_ui()

    def _init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setSpacing(6)

        # Baris pilihan mode
        mode_box = QGroupBox("Mode Pemilihan")
        mode_layout = QHBoxLayout()
        self.rb_single = QRadioButton("Tunggal")
        self.rb_multi = QRadioButton("Ganda")
        self.rb_single.setChecked(True)
        self.rb_single.toggled.connect(self._on_mode_toggled)
        self.rb_multi.toggled.connect(self._on_mode_toggled)
        mode_layout.addWidget(self.rb_single)
        mode_layout.addWidget(self.rb_multi)
        mode_layout.addStretch(1)
        mode_box.setLayout(mode_layout)
        main_layout.addWidget(mode_box)

        # Grid metode
        group = QGroupBox("METODE")
        layout = QGridLayout()
        self.methods = [
            ("Thresholding", {"threshold": 128}),
            ("Thresholding Double", {"t1": 50, "t2": 150}),
            ("Grayscale", {}),
            ("Negative", {}),
            ("Brightness", {"value": 0}),
            ("Contrast", {"factor": 1.0}),
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

        self.btn_group = QButtonGroup(self)
        self.btn_group.setExclusive(True)

        row, col = 0, 0
        for name, params in self.methods:
            cb = QCheckBox(name)
            cb.method_name = name
            cb.default_params = params
            cb.toggled.connect(self._on_method_toggled)
            self.btn_group.addButton(cb)
            self.radio_buttons[name] = cb
            layout.addWidget(cb, row, col)
            col += 1
            if col == 3:
                col = 0
                row += 1

        group.setLayout(layout)
        main_layout.addWidget(group)
        self.setLayout(main_layout)

    def _on_mode_toggled(self, checked: bool):
        if not checked:
            return
        multi = self.rb_multi.isChecked()
        if multi != self.mode_multi:
            self.mode_multi = multi
            # Berpindah mode selalu menghapus semua pilihan
            self.clear_selection()
            self.btn_group.setExclusive(not multi)

    def _on_method_toggled(self, checked: bool):
        cb = self.sender()
        name = cb.method_name

        if self.mode_multi:
            if checked:
                if len(self._selected_order) >= self.MAX_METHODS:
                    cb.blockSignals(True)
                    cb.setChecked(False)
                    cb.blockSignals(False)
                    self.limit_exceeded.emit()
                    return
                if name not in self._selected_order:
                    self._selected_order.append(name)
            else:
                if name in self._selected_order:
                    self._selected_order.remove(name)
        else:
            if checked:
                self._selected_order = [name]

        self._refresh_labels()
        self._emit_selection()

    def _refresh_labels(self):
        """Tampilkan urutan pada label metode terpilih (mode ganda)."""
        for i, name in enumerate(self._selected_order, start=1):
            self.radio_buttons[name].setText(f"{i}. {name}")
        for name, _ in self.methods:
            if name not in self._selected_order:
                self.radio_buttons[name].setText(name)

    def _emit_selection(self):
        sel = [
            (name, self.radio_buttons[name].default_params)
            for name in self._selected_order
        ]
        self.methods_changed.emit(sel)

    def clear_selection(self):
        """Menghilangkan semua pilihan metode (semua mode)."""
        # Qt: pada QButtonGroup eksklusif, setChecked(False) tidak berlaku
        # saat sinyal diblokir -> nonaktifkan eksklusivitas sementara.
        was_exclusive = self.btn_group.exclusive()
        self.btn_group.setExclusive(False)
        for cb in self.radio_buttons.values():
            cb.blockSignals(True)
            cb.setChecked(False)
            cb.blockSignals(False)
        self.btn_group.setExclusive(was_exclusive)
        self._selected_order = []
        self._refresh_labels()
        self._emit_selection()