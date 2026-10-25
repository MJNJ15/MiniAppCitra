import cv2
import numpy as np
from .base_processor import BaseProcessor

class EmbossProcessor(BaseProcessor):
    def process(self, image: np.ndarray, **kwargs) -> np.ndarray:
        kernel = np.array([[-2, -1, 0], 
                           [-1,  1, 1], 
                           [ 0,  1, 2]])
        # Filter2D bekerja dengan baik pada citra grayscale untuk efek emboss
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
        result = cv2.filter2D(gray, -1, kernel)
        return np.clip(result + 128, 0, 255).astype(np.uint8) # Shift agar terlihat di layar