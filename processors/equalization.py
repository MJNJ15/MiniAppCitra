import cv2
import numpy as np
from .base_processor import BaseProcessor

class EqualizationProcessor(BaseProcessor):
    def process(self, image: np.ndarray, **kwargs) -> np.ndarray:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
        return cv2.equalizeHist(gray)