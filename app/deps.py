from __future__ import annotations
from typing import Annotated
from fastapi import Depends
from app.crypto.base import Encryptor
from app.crypto.base64_json import Base64JsonEncryptor
from app.signature.base import Signer
from app.config import settings
from app.signature.hmac_sha256 import HmacSha256Signer
from app.errors import APIError

def get_encryptor() -> Encryptor:
    """Factory for the Encryptor used by the routes.


    Swap this implementation to change the encryption algorithm globally
    without touching route logic.
    """
    return Base64JsonEncryptor()

def get_signer() -> Signer:
    """Factory for the Signer used by the routes.


    Reads RIOT_HMAC_SECRET from environment and returns an HMAC-based signer.
    """
    if not settings.hmac_secret:
        # Réponse API propre plutôt qu'un ValueError 500
        raise APIError(status_code=503, code="secret_missing", message="HMAC secret missing")
    return HmacSha256Signer(secret=settings.hmac_secret.encode("utf-8"))

# Typed FastAPI dependencies for better readability in route signatures
EncryptorDep = Annotated[Encryptor, Depends(get_encryptor)]
SignerDep = Annotated[Signer, Depends(get_signer)]
