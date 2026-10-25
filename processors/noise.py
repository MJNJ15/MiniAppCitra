import cv2
import numpy as np
from .base_processor import BaseProcessor


class NoiseProcessor(BaseProcessor):
    def process(self, image: np.ndarray, **kwargs) -> np.ndarray:
        noise_type = kwargs.get('type', 'Gaussian')
        amount = kwargs.get('amount', 0.1)
        
        # Konversi ke float32 di awal agar operasi aritmatika aman
        img_float = image.astype(np.float32)
        
        if noise_type == "Gaussian":
            # amount (0.0 - 1.0) di-map ke standard deviation (0 - 50)
            sigma = amount * 50
            mean = 0
            gauss = np.random.normal(mean, sigma, image.shape).astype(np.float32)
            result = img_float + gauss  # Sekarang keduanya float32, aman!
            
        elif noise_type == "Salt & Pepper":
            result = np.copy(img_float)
            s_vs_p = 0.5
            
            # Salt (piksel putih)
            num_salt = np.ceil(amount * image.size * s_vs_p)
            coords = [np.random.randint(0, i - 1, int(num_salt)) for i in image.shape]
            result[tuple(coords)] = 255.0
            
            # Pepper (piksel hitam)
            num_pepper = np.ceil(amount * image.size * (1.0 - s_vs_p))
            coords = [np.random.randint(0, i - 1, int(num_pepper)) for i in image.shape]
            result[tuple(coords)] = 0.0
        else:
            result = img_float
        
        # Clip ke rentang [0, 255] lalu konversi kembali ke uint8
        return np.clip(result, 0, 255).astype(np.uint8)