"""Abstract implementation for models"""
from abc import ABC, abstractmethod


class Model(ABC):
    """Abstract class for models"""

    def __init__(self):
        self.is_loaded = False
        self.model = None
        self.tokenizer = None

    def load_model(self):
        """Load model weights"""
        if not self.is_loaded:
            self._load_model()
            self.is_loaded = True

    @abstractmethod
    def _load_model(self):
        pass

    @abstractmethod
    def inference(self, *args, **kwargs):
        """Run model inference"""
