from __future__ import annotations
import logging
from typing import Any, Dict
from fastapi import FastAPI, HTTPException, Request, Body, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.deps import EncryptorDep, SignerDep
from app.models import VerifyInput, SignOutput
from app.config import settings
from app.middleware.request_id import RequestIdMiddleware
from app.errors import add_exception_handlers, APIError


# Logging
logger = logging.getLogger('riot-crypto-api')
logger.setLevel(settings.log_level)


# App initialization
app = FastAPI(
    title='Riot Take-Home Crypto API',
    version='1.0.0',
    description=(
        'HTTP API with 4 endpoints:\n'
        '- POST /encrypt: Base64(JSON(value)) on all depth-1 properties\n'
        '- POST /decrypt: Attempt Base64+JSON decode on depth-1 string values\n'
        '- POST /sign: HMAC-SHA256 over canonical JSON value\n'
        '- POST /verify: 204 if signature matches, 400 otherwise\n\n'
        'Algorithms are abstracted for easy swapping.'
    ),
)


# Body size limiting middleware
MAX_BYTES = settings.max_body_bytes

class BodySizeLimiter(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        cl = request.headers.get('content-length')
        try:
            if cl is not None and int(cl) > MAX_BYTES:
                raise APIError(status_code=413, code='payload_too_large', message='Payload too large')
        except ValueError:
            raise APIError(status_code=400, code='invalid_content_length', message='Invalid Content-Length')
        return await call_next(request)

app.add_middleware(RequestIdMiddleware)
app.add_middleware(BodySizeLimiter)
add_exception_handlers(app)


# Health endpoints
@app.get('/health/live')
async def live() -> dict:
    """Liveness probe: returns 200 if process is alive."""
    return {'status': 'ok'}

@app.get('/health/ready')
async def ready() -> dict:
    """Readiness probe: ensure required config (e.g., secret) is present."""
    if not settings.hmac_secret:
        raise HTTPException(status_code=503, detail='HMAC secret missing')
    return {'status': 'ready'}


# Helpers
def _ensure_object(payload: Any) -> Dict[str, Any]:
    """Ensure the root payload is a JSON object."""
    if not isinstance(payload, dict):
        raise APIError(status_code=400, code='root_not_object', message='Payload must be a JSON object at the root.')
    return payload


# API routes
@app.post('/encrypt', summary='Encrypt depth-1 properties using Base64(JSON(value))')
async def encrypt(
    encryptor: EncryptorDep, payload: Dict[str, Any] = Body(..., embed=False)):
    """Encrypt all top-level properties.

    For each key at depth 1, the *value* is serialized to JSON and encoded in
    Base64, producing a string token. The response is an object where every
    top-level value is now a Base64 string.
    """
    obj = _ensure_object(payload)
    result: Dict[str, Any] = {k: encryptor.encrypt_value(v) for k, v in obj.items()}
    return JSONResponse(content=result)


@app.post('/decrypt', summary='Decrypt depth-1 Base64(JSON(value)) tokens; leave others unchanged')
async def decrypt(encryptor: EncryptorDep, payload: Dict[str, Any] = Body(..., embed=False)):
    """Attempts to decrypt all top-level *string* values.

    If a string value is a valid Base64(JSON(value)) token, replace it with the
    decoded original value (type preserved). If not valid (or not a string),
    leave the property unchanged, matching the challenge requirement.
    """
    obj = _ensure_object(payload)
    result: Dict[str, Any] = {}
    for k, v in obj.items():
        if isinstance(v, str):
            try:
                result[k] = encryptor.decrypt_value(v)
            except Exception:
                result[k] = v
        else:
            result[k] = v
    return JSONResponse(content=result)


@app.post('/sign', response_model=SignOutput, summary='Sign payload with HMAC-SHA256 over canonical JSON')
async def sign(signer: SignerDep, payload: Any = Body(..., embed=False)):
    """Compute an order-independent signature for *payload*.

    The signature is computed over canonical JSON bytes so that different key
    orders produce the same signature. This endpoint accepts *any* JSON value
    (object, array, string, number, ...), per challenge statement.
    """
    signature = signer.sign(payload)
    return SignOutput(signature=signature)


@app.post('/verify', summary='Verify signature against payload', status_code=204)
async def verify(body: VerifyInput, signer: SignerDep):
    """Return 204 No Content if signature matches the provided *data*.

    Returns 400 Bad Request if verification fails. Input validation guarantees
    that `data` is a JSON object and `signature` is non-empty.
    """
    ok = signer.verify(body.signature, body.data)
    if not ok:
        raise APIError(status_code=400, code='invalid_signature', message='Invalid signature')
    return Response(status_code=204)
