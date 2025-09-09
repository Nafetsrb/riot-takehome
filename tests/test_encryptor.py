import pytest
from app.crypto.base64_json import Base64JsonEncryptor


def test_round_trip_primitive():
    enc = Base64JsonEncryptor()
    token = enc.encrypt_value("John Doe")
    assert isinstance(token, str)
    assert enc.decrypt_value(token) == "John Doe"


def test_round_trip_number():
    enc = Base64JsonEncryptor()
    token = enc.encrypt_value(30)
    assert enc.decrypt_value(token) == 30


def test_round_trip_object():
    enc = Base64JsonEncryptor()
    obj = {"email": "john@example.com", "phone": "123-456-7890"}
    token = enc.encrypt_value(obj)
    assert enc.decrypt_value(token) == obj


def test_invalid_token_raises():
    enc = Base64JsonEncryptor()
    with pytest.raises(Exception):
        enc.decrypt_value("not-base64!!")
