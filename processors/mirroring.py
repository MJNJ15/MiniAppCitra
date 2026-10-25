import cv2
import numpy as np
from .base_processor import BaseProcessor

class MirroringProcessor(BaseProcessor):
    def process(self, image: np.ndarray, **kwargs) -> np.ndarray:
        direction = kwargs.get('direction', 'Horizontal')
        
        # flipCode: 1 = Horizontal, 0 = Vertical, -1 = Both
        if direction == "Horizontal":
            flip_code = 1
        elif direction == "Vertical":
            flip_code = 0
        elif direction == "Both":
            flip_code = -1
        else:
            flip_code = 1
            
        return cv2.flip(image, flip_code)