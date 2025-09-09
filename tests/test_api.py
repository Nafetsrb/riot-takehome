import os

# Define the HMAC secret BEFORE importing the app so that
# the configuration is available when dependencies are initialized.
os.environ["RIOT_HMAC_SECRET"] = "test-secret"

from fastapi.testclient import TestClient  # noqa: E402
from app.main import app  # noqa: E402

client = TestClient(app)


def test_encrypt_decrypt_round_trip():
    """
    Verify that encrypting a JSON object and then decrypting it
    restores the exact original payload.
    """
    payload = {
        "name": "John Doe",
        "age": 30,
        "contact": {"email": "john@example.com", "phone": "123-456-7890"},
    }

    # Encrypt the payload
    enc_res = client.post("/encrypt", json=payload)
    assert enc_res.status_code == 200
    enc = enc_res.json()
    # All values should now be Base64-encoded strings
    assert isinstance(enc["name"], str)
    assert isinstance(enc["age"], str)
    assert isinstance(enc["contact"], str)

    # Decrypt back the encrypted payload
    dec_res = client.post("/decrypt", json=enc)
    assert dec_res.status_code == 200
    # The decrypted payload should equal the original input
    assert dec_res.json() == payload


def test_decrypt_leaves_unencrypted_unchanged():
    """
    Ensure that properties that are not valid Base64 tokens
    remain unchanged when passed to /decrypt.
    """
    # Encrypt only the "name" field
    name_enc = client.post("/encrypt", json={"name": "John Doe"}).json()["name"]
    mixed = {"name": name_enc, "birth_date": "1998-11-19"}

    # Decrypt the mixed payload
    res = client.post("/decrypt", json=mixed)
    assert res.status_code == 200
    body = res.json()
    # "name" should be decrypted, "birth_date" should remain unchanged
    assert body["name"] == "John Doe"
    assert body["birth_date"] == "1998-11-19"


def test_sign_and_verify_success_204_no_body():
    """
    Verify that signing a payload produces a valid signature
    that can be successfully verified by /verify.
    Response must be 204 No Content with an empty body.
    """
    data = {"message": "Hello World", "timestamp": 1616161616}
    sig_res = client.post("/sign", json=data)
    assert sig_res.status_code == 200
    signature = sig_res.json()["signature"]

    # Verify the signature
    ver_res = client.post("/verify", json={"signature": signature, "data": data})
    assert ver_res.status_code == 204
    # 204 responses must have an empty body
    assert ver_res.text == ""


def test_verify_order_independent():
    """
    The signature must be independent of the property order in the JSON object.
    """
    a = {"message": "Hello World", "timestamp": 1616161616}
    b = {"timestamp": 1616161616, "message": "Hello World"}
    signature = client.post("/sign", json=a).json()["signature"]

    # Both JSONs should validate against the same signature
    res = client.post("/verify", json={"signature": signature, "data": b})
    assert res.status_code == 204


def test_verify_fail_on_tamper():
    """
    Verify must fail (400) if the payload is altered after signing.
    """
    original = {"message": "Hello World", "timestamp": 1616161616}
    signature = client.post("/sign", json=original).json()["signature"]
    tampered = {"message": "Goodbye World", "timestamp": 1616161616}

    res = client.post("/verify", json={"signature": signature, "data": tampered})
    assert res.status_code == 400
    body = res.json()
    assert body.get("code") == "invalid_signature"


# ------------------------------
# Validation / error cases
# ------------------------------

def test_encrypt_rejects_non_object_root():
    """
    /encrypt should reject payloads where the root is not a JSON object.
    FastAPI/Pydantic should return 422.
    """
    res = client.post("/encrypt", json=["not", "an", "object"])
    assert res.status_code == 422


def test_decrypt_rejects_non_object_root():
    """
    /decrypt should reject payloads where the root is not a JSON object.
    FastAPI/Pydantic should return 422.
    """
    res = client.post("/decrypt", json="not-an-object")
    assert res.status_code == 422


def test_verify_missing_fields_returns_422():
    """
    /verify requires both 'signature' and 'data'.
    Missing 'data' should cause a 422 validation error.
    """
    res = client.post("/verify", json={"signature": "abc"})
    assert res.status_code == 422


def test_verify_rejects_non_object_data():
    """
    /verify requires 'data' to be a JSON object (dict).
    Arrays or other types should cause a 422 validation error.
    """
    sig = client.post("/sign", json={"x": 1}).json()["signature"]
    res = client.post("/verify", json={"signature": sig, "data": [1, 2, 3]})
    assert res.status_code == 422
