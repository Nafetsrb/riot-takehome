# Riot Crypto API (Take-Home) — Fully Commented & Hardened

HTTP API with 4 endpoints: `/encrypt`, `/decrypt`, `/sign`, `/verify`.

---

## Design Patterns & Architecture

- **Strategy pattern** for algorithms:
  - `Encryptor` (Base64 implementation: `Base64JsonEncryptor`)
  - `Signer` (HMAC-SHA256 implementation: `HmacSha256Signer`)
  - Both are injected via factories in `app/deps.py`, making algorithms easily swappable.
- **Dependency Injection**: `Depends(get_encryptor/get_signer)` decouples routes from concrete implementations.
- **Canonicalization**: `orjson` with sorted keys ensures **order-independent signatures**.
- **Configuration**: `app/config.py` uses **pydantic-settings**.
  - `RIOT_HMAC_SECRET` → HMAC key (must be set in `.env` or environment).
  - `APP_LOG_LEVEL` → logging level (default: INFO, you can also put CRITICAL, ERROR, WARNING or DEBUG).
  - `APP_MAX_BODY_BYTES` → request size limit (default: 2 MiB).
- **Cross-cutting concerns**:
  - Middleware: request ID (`X-Request-ID`) and body-size limit.
  - Centralized error handling: `APIError` → normalized JSON error body.
- **Stateless**: horizontally scalable.

---

## API Endpoints

### POST `/encrypt`
- **Input**: JSON **object**
- **Output**: depth-1 values replaced by **Base64(JSON(value))**
- **Validation**: non-object roots → **422 Unprocessable Entity**

### POST `/decrypt`
- **Input**: JSON **object**
- **Output**: depth-1 string values are decoded if valid Base64(JSON(value)), otherwise left unchanged
- **Validation**: non-object roots → **422**

### POST `/sign`
- **Input**: **any JSON value** (object, array, string, number, etc.)
- **Output**: `{ "signature": "<hex>" }`

### POST `/verify`
- **Input**: 
  ```json
  {
    "signature": "hex-string",
    "data": { "must": "be an object" }
  }
  ```
- **Output**:
  - **204 No Content** if signature is valid (no response body).
  - **400 invalid_signature** if verification fails.
  - **422** for validation errors (missing fields, wrong types, `data` not an object).

---

## Swagger UI & Documentation
- **Interactive API docs**: available at [http://localhost:8000/docs](http://localhost:8000/docs)  
- **ReDoc documentation**: available at [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## Security & Config

- **Secret management**:  
  - `RIOT_HMAC_SECRET` must be provided via environment variable or `.env` file.  
  - `/health/ready` returns **503** if the secret is missing.
- **Body size limit**:  
  - Controlled by `APP_MAX_BODY_BYTES` (default: 2 MiB).
- **Error format**:  
  - All errors return structured JSON:  
    ```json
    { "error": "message", "code": "error_code" }
    ```

---

## Run Locally

```bash
python -m venv .venv
source .venv/bin/activate   # or .venv\Scripts\activate on Windows

pip install -r requirements.txt

cp .env.example .env
# edit .env and set RIOT_HMAC_SECRET, APP_LOG_LEVEL, APP_MAX_BODY_BYTES

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

## Tests

We use `pytest` for both unit and integration tests.  
Tests cover:
- Round-trip encryption/decryption.
- Signature consistency and verification.
- Error handling and validation edge cases.

Run all tests:
```bash
pytest
```

Verbose output with detailed test names:
```bash
pytest -vv -s --tb=short
```

---

## Postman Collection

A Postman collection is included (`postman_collection.json`), you can directly import it in the Postman application.

