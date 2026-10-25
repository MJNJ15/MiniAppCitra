import cv2
import numpy as np
from .base_processor import BaseProcessor

class NegativeProcessor(BaseProcessor):
    def process(self, image: np.ndarray, **kwargs) -> np.ndarray:
        # Inversi semua nilai piksel (255 - pixel)
        return cv2.bitwise_not(image)