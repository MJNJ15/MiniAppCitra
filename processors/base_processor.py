from abc import ABC, abstractmethod
import numpy as np

class BaseProcessor(ABC):
    """
    Kelas abstrak dasar untuk semua processor pengolahan citra.
    Setiap metode pengolahan wajib mewarisi kelas ini.
    """

    @abstractmethod
    def process(self, image: np.ndarray, **kwargs) -> np.ndarray:
        """
        Memproses citra input dan mengembalikan citra hasil.

        Args:
            image (np.ndarray): Citra input dalam format numpy array (BGR dari OpenCV).
            **kwargs: Parameter dinamis spesifik untuk setiap processor 
                      (misal: threshold_value, kernel_size, angle).

        Returns:
            np.ndarray: Citra hasil pengolahan dalam format numpy array.
        """
        pass

    def get_name(self) -> str:
        """Mengembalikan nama human-readable dari processor."""
        return self.__class__.__name__.replace('_', ' ').title()