"""Tema visual modern (gelap) untuk MiniAppCitra.

Diterapkan via QApplication.setStyleSheet di main.py.
Warna aksen: biru #4a8fe7 (Proses), hijau #43a047 (Webcam),
oranye #fb8c00 (Reset), abu #546e7a (Ambil Foto).
"""

APP_STYLE = """
* {
    font-family: "Segoe UI", "Roboto", "Inter", sans-serif;
    font-size: 13px;
}

QMainWindow, QDialog {
    background-color: #1e222a;
}

QWidget {
    color: #e6e9ef;
    background-color: transparent;
}

QToolBar {
    background-color: #20252e;
    border-bottom: 1px solid #363e4c;
    padding: 4px;
    spacing: 6px;
}

QToolBar QToolButton {
    background: transparent;
    border: none;
    border-radius: 6px;
    padding: 6px 12px;
    color: #cfd6e0;
    font-weight: 600;
}

QToolBar QToolButton:hover {
    background-color: #2f3744;
}

QToolBar QToolButton:pressed {
    background-color: #232a34;
}

QGroupBox {
    background-color: #242a34;
    border: 1px solid #363e4c;
    border-radius: 10px;
    margin-top: 14px;
    padding: 12px 8px 8px 8px;
    font-weight: 600;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    top: 2px;
    padding: 0 6px;
    color: #9aa4b2;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 1px;
}

QPushButton {
    background-color: #2f3744;
    color: #e6e9ef;
    border: 1px solid #434e60;
    border-radius: 8px;
    padding: 8px 14px;
    font-weight: 600;
}

QPushButton:hover {
    background-color: #3a4554;
}

QPushButton:pressed {
    background-color: #232a34;
}

QPushButton:disabled {
    background-color: #2a303a;
    color: #6b7480;
    border-color: #333b47;
}

QSpinBox, QDoubleSpinBox, QComboBox {
    background-color: #1f242e;
    border: 1px solid #3a4352;
    border-radius: 6px;
    padding: 4px 8px;
    selection-background-color: #4a8fe7;
}

QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {
    border: 1px solid #4a8fe7;
}

QComboBox::drop-down {
    border: none;
    width: 22px;
}

QComboBox QAbstractItemView {
    background-color: #242a34;
    border: 1px solid #3a4352;
    selection-background-color: #4a8fe7;
    outline: none;
}

QSlider::groove:horizontal {
    height: 4px;
    background: #3a4352;
    border-radius: 2px;
}

QSlider::sub-page:horizontal {
    background: #4a8fe7;
    border-radius: 2px;
}

QSlider::handle:horizontal {
    width: 14px;
    height: 14px;
    margin: -5px 0;
    border-radius: 7px;
    background: #4a8fe7;
}

QSlider::handle:horizontal:hover {
    background: #6ea6f2;
}

QCheckBox, QRadioButton {
    spacing: 6px;
    font-weight: 500;
}

QCheckBox::indicator, QRadioButton::indicator {
    width: 15px;
    height: 15px;
    border: 1px solid #566073;
    border-radius: 4px;
    background: #1f242e;
}

QCheckBox::indicator:hover, QRadioButton::indicator:hover {
    border-color: #4a8fe7;
}

QCheckBox::indicator:checked {
    background: #4a8fe7;
    border-color: #4a8fe7;
}

QRadioButton::indicator {
    border-radius: 8px;
}

QRadioButton::indicator:checked {
    background: #4a8fe7;
    border: 4px solid #1f242e;
}

QScrollArea {
    border: none;
    background: transparent;
}

QScrollBar:vertical {
    background: transparent;
    width: 10px;
    margin: 2px;
}

QScrollBar::handle:vertical {
    background: #3a4352;
    border-radius: 5px;
    min-height: 24px;
}

QScrollBar::handle:vertical:hover {
    background: #4a8fe7;
}

QScrollBar::add-line, QScrollBar::sub-line {
    height: 0;
    width: 0;
}

QStatusBar {
    background-color: #20252e;
    color: #9aa4b2;
    border-top: 1px solid #363e4c;
}

QStatusBar::item {
    border: none;
}

QToolTip {
    background-color: #2f3744;
    color: #e6e9ef;
    border: 1px solid #434e60;
    border-radius: 4px;
    padding: 4px 8px;
}
"""


def apply_app_style(app) -> None:
    """Terapkan tema modern ke QApplication."""
    app.setStyleSheet(APP_STYLE)
