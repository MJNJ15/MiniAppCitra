import cv2
import numpy as np
from PySide6.QtGui import QImage, QPixmap

def cv2_to_qpixmap(cv_img: np.ndarray) -> QPixmap:
    """
    Mengkonversi citra OpenCV (NumPy array) menjadi QPixmap untuk ditampilkan di QLabel.
    Menangani citra berwarna (3 channel) dan citra grayscale (2 channel).
    """
    if cv_img is None or cv_img.size == 0:
        return QPixmap()

    # Jika citra berwarna, konversi dari BGR ke RGB
    if len(cv_img.shape) == 3:
        rgb_img = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_img.shape
        bytes_per_line = ch * w
        q_img = QImage(rgb_img.data, w, h, bytes_per_line, QImage.Format_RGB888)
    # Jika citra grayscale
    elif len(cv_img.shape) == 2:
        h, w = cv_img.shape
        bytes_per_line = w
        q_img = QImage(cv_img.data, w, h, bytes_per_line, QImage.Format_Grayscale8)
    else:
        return QPixmap()

    # .copy() sangat penting untuk memisahkan memori QImage dari NumPy array
    # agar tidak terjadi crash saat NumPy array di-garbage collect.
    return QPixmap.fromImage(q_img.copy())

def qpixmap_to_cv2(pixmap: QPixmap) -> np.ndarray:
    """
    Mengkonversi QPixmap kembali menjadi citra OpenCV (NumPy array BGR).
    Digunakan jika kita perlu memproses ulang citra yang sudah dimodifikasi di UI.
    """
    if pixmap.isNull():
        return None

    q_img = pixmap.toImage()
    width = q_img.width()
    height = q_img.height()
    
    # Konversi QImage ke pointer bytes
    ptr = q_img.bits()
    ptr.setsize(height * width * 4) # Format_ARGB32 selalu 4 channel
    
    # Konversi ke numpy array
    arr = np.frombuffer(ptr, np.uint8).reshape((height, width, 4))
    
    # Konversi dari RGBA ke BGR (format OpenCV)
    cv_img = cv2.cvtColor(arr, cv2.COLOR_RGBA2BGR)
    return cv_img