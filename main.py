import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

from ui.main_window import MainWindow
from ui.styles import apply_app_style


def main() -> None:
    # High-DPI scaling agar antarmuka tajam di layar berdensitas tinggi
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)

    app = QApplication(sys.argv)
    app.setStyle("Fusion")       # style dasar yang konsisten lintas platform
    apply_app_style(app)         # tema modern gelap kustom

    window = MainWindow()
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()