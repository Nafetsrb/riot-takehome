from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any

class Encryptor(ABC):
    """Abstract interface for a depth-1 property encryptor.


    Concrete implementations must convert *any* JSON value to an encrypted
    string token, and be able to decrypt that token back to the original value
    (type preserved).
    """

    @abstractmethod
    def encrypt_value(self, value: Any) -> str:
        """Encrypt a single JSON value into a string token.


        Args:
        value: Any JSON-serializable Python object.
        Returns:
        str: Opaque token representing the encrypted value.
        """
        raise NotImplementedError

    @abstractmethod
    def decrypt_value(self, token: str) -> Any:
        """Decrypt a string token back into the original JSON value.


        Args:
        token: The string produced by :meth:`encrypt_value`.
        Returns:
        Any: The original JSON value.
        Raises:
        Exception: If token is invalid (callers may choose to keep original).
        """
        raise NotImplementedError
