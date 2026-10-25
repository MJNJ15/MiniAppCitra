import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

# Pastikan import dilakukan dari root package
from ui.main_window import MainWindow

def main():
    # Mengaktifkan dukungan High-DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    
    app = QApplication(sys.argv)
    
    # Menggunakan style 'Fusion' untuk tampilan yang konsisten dan modern di semua OS
    app.setStyle("Fusion") 
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()