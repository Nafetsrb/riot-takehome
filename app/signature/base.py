from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any

class Signer(ABC):
    """Abstract interface for signing and verifying JSON values.


    Implementations must be order-independent: the same JSON semantics should
    yield the same signature even if property orders differ.
    """
    @abstractmethod
    def sign(self, data: Any) -> str:
        """Compute a signature for *data*.


        Args:
        data: JSON-serializable value to sign.
        Returns:
        str: Signature string (algorithm-dependent; hex for HMAC-SHA256).
        """
        raise NotImplementedError
    @abstractmethod
    def verify(self, signature: str, data: Any) -> bool:
        """Check whether *signature* matches *data*.


        Returns:
        bool: True if valid, False otherwise.
        """
        raise NotImplementedError
