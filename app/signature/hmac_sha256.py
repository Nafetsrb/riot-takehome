from __future__ import annotations
import hmac, hashlib
from typing import Any
from app.utils.json_canonical import canonicalize
from .base import Signer

class HmacSha256Signer(Signer):
    """Signer that computes HMAC-SHA256 over canonical JSON bytes.


    The use of canonical JSON ensures order-independent signatures, satisfying
    the requirement that property reordering must not change the signature.
    """

    def __init__(self, secret: bytes):
        if not secret:
            raise ValueError('HMAC secret must not be empty')
        self._secret = secret

    def sign(self, data: Any) -> str:
        """Return hex-encoded HMAC-SHA256 signature for *data*."""
        msg = canonicalize(data)
        return hmac.new(self._secret, msg, hashlib.sha256).hexdigest()

    def verify(self, signature: str, data: Any) -> bool:
        """Return True if *signature* matches *data*, else False.


        Uses hmac.compare_digest for constant-time comparison.
        """
        expected = self.sign(data)
        return hmac.compare_digest(expected, signature)
