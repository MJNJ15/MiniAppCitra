import cv2
import numpy as np
from .base_processor import BaseProcessor

class ConvolutionProcessor(BaseProcessor):
    def process(self, image: np.ndarray, **kwargs) -> np.ndarray:
        kernel_list = kwargs.get('kernel', [[0,0,0],[0,1,0],[0,0,0]])
        kernel = np.array(kernel_list, dtype=np.float32)
        
        # Gunakan filter2D untuk konvolusi
        # depth=-1 berarti output memiliki kedalaman yang sama dengan input
        return cv2.filter2D(image, -1, kernel)