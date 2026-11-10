"""Kelas dasar untuk semua processor pengolahan citra."""
from abc import ABC, abstractmethod

import numpy as np


class BaseProcessor(ABC):
    """Kontrak wajib untuk setiap metode pengolahan citra."""

    @abstractmethod
    def process(self, image: np.ndarray, **kwargs) -> np.ndarray:
        """Proses citra BGR dan kembalikan citra hasil."""
        pass