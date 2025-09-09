from __future__ import annotations
import base64
import orjson
from typing import Any
from .base import Encryptor

class Base64JsonEncryptor(Encryptor):
    """Depth-1 encryptor using Base64(JSON(value)).


    Rationale
    ---------
    The challenge requires encrypting *top-level* properties (depth=1) using
    Base64 for simplicity. To guarantee perfect round-trip of types (e.g.
    numbers, booleans, nested objects), we serialize the *value itself* to JSON
    and then Base64-encode the resulting bytes. Decrypt reverses the process.
    """

    def encrypt_value(self, value: Any) -> str:
        """Serialize *value* to JSON and Base64-encode it.


        Returns:
        str: A Base64 string token that represents the JSON-encoded value.
        """
        payload = orjson.dumps(value)
        return base64.b64encode(payload).decode('utf-8')

    def decrypt_value(self, token: str) -> Any:
        """Decode Base64 token and parse the JSON payload back to Python.


        Args:
        token: Base64-encoded JSON string.
        Returns:
        Any: Original JSON value.
        Raises:
        Exception: If token is invalid (non Base64 or invalid JSON). The
        caller decides whether to swallow the error and keep the
        original value unchanged (as per spec).
        """
        raw = base64.b64decode(token.encode('utf-8'), validate=True)
        return orjson.loads(raw)
