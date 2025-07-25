from abc import ABC, abstractmethod
from models import NormalizedHost


class BaseNormalizer(ABC):

    @abstractmethod
    def normalize(self, raw_host: dict) -> NormalizedHost:
        """Convert raw vendor-specific host into NormalizedHost"""
        pass
