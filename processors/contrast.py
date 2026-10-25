import cv2
import numpy as np
from .base_processor import BaseProcessor

class ContrastProcessor(BaseProcessor):
    def process(self, image: np.ndarray, **kwargs) -> np.ndarray:
        factor = kwargs.get('factor', 1.0)
        # Rumus: factor * (pixel - 128) + 128
        img_float = image.astype(np.float32)
        result = factor * (img_float - 128) + 128
        return np.clip(result, 0, 255).astype(np.uint8)