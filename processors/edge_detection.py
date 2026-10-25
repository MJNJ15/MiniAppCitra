import cv2
import numpy as np
from .base_processor import BaseProcessor

class EdgeDetectionProcessor(BaseProcessor):
    def process(self, image: np.ndarray, **kwargs) -> np.ndarray:
        method = kwargs.get('edge_method', 'Canny')
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
        
        if method == "Canny":
            return cv2.Canny(gray, 100, 200)
        elif method == "Sobel X":
            sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
            return np.absolute(sobelx).astype(np.uint8)
        elif method == "Sobel Y":
            sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
            return np.absolute(sobely).astype(np.uint8)
        return gray