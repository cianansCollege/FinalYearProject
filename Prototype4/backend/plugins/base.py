"""Abstract plugin contract that every backend model implementation must follow."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class ModelPlugin(ABC):
    id: str
    name: str
    description: str

    @abstractmethod
    def predict(self, wav_bytes: bytes) -> dict[str, Any]:
        raise NotImplementedError
