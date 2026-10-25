import cv2
import numpy as np
from .base_processor import BaseProcessor

class SharpeningProcessor(BaseProcessor):
    def process(self, image: np.ndarray, **kwargs) -> np.ndarray:
        kernel = np.array([[0, -1, 0], 
                           [-1, 5, -1], 
                           [0, -1, 0]])
        return cv2.filter2D(image, -1, kernel)