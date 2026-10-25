import cv2
import numpy as np
from .base_processor import BaseProcessor

class RotationProcessor(BaseProcessor):
    def process(self, image: np.ndarray, **kwargs) -> np.ndarray:
        angle = kwargs.get('angle', 0)
        h, w = image.shape[:2]
        center = (w // 2, h // 2)
        
        # Mendapatkan matriks rotasi
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        
        # Menghitung dimensi bounding box baru agar citra tidak terpotong
        cos = np.abs(M[0, 0])
        sin = np.abs(M[0, 1])
        new_w = int((h * sin) + (w * cos))
        new_h = int((h * cos) + (w * sin))
        
        # Menyesuaikan matriks translasi
        M[0, 2] += (new_w / 2) - center[0]
        M[1, 2] += (new_h / 2) - center[1]
        
        # Melakukan warp affine, mengisi area kosong dengan putih (255, 255, 255)
        return cv2.warpAffine(image, M, (new_w, new_h), borderValue=(255, 255, 255))