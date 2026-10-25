import cv2
import numpy as np
from .base_processor import BaseProcessor

class ThresholdingProcessor(BaseProcessor):
    def process(self, image: np.ndarray, **kwargs) -> np.ndarray:
        threshold = kwargs.get('threshold', 128)
        # Konversi ke grayscale jika citra berwarna
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
        _, result = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY)
        return result

class DoubleThresholdingProcessor(BaseProcessor):
    def process(self, image: np.ndarray, **kwargs) -> np.ndarray:
        t1 = kwargs.get('t1', 50)
        t2 = kwargs.get('t2', 150)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
        
        # Logika: jika T1 <= pixel <= T2, maka 255, selain itu 0
        result = np.where((gray >= t1) & (gray <= t2), 255, 0).astype(np.uint8)
        return result