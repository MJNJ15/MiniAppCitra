import cv2
import numpy as np
from .base_processor import BaseProcessor

class BrightnessProcessor(BaseProcessor):
    def process(self, image: np.ndarray, **kwargs) -> np.ndarray:
        value = kwargs.get('value', 0)
        # cv2.add secara otomatis melakukan clipping ke [0, 255]
        return cv2.add(image, value)