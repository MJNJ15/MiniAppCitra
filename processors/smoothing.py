import cv2
import numpy as np
from .base_processor import BaseProcessor

class SmoothingProcessor(BaseProcessor):
    def process(self, image: np.ndarray, **kwargs) -> np.ndarray:
        kernel_size = kwargs.get('kernel_size', 3)
        # Pastikan kernel_size ganjil
        if kernel_size % 2 == 0:
            kernel_size += 1
            
        method = kwargs.get('type', 'Gaussian')
        
        if method == "Average":
            return cv2.blur(image, (kernel_size, kernel_size))
        elif method == "Gaussian":
            return cv2.GaussianBlur(image, (kernel_size, kernel_size), 0)
        elif method == "Median":
            return cv2.medianBlur(image, kernel_size)
        return image