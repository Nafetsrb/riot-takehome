from app.signature.hmac_sha256 import HmacSha256Signer


def test_sign_order_independent():
    signer = HmacSha256Signer(b"secret")
    a = {"message": "Hello World", "timestamp": 1616161616}
    b = {"timestamp": 1616161616, "message": "Hello World"}
    assert signer.sign(a) == signer.sign(b)


def test_verify_true_false():
    signer = HmacSha256Signer(b"secret")
    data = {"x": 1, "y": [2, 3], "z": {"a": True}}
    sig = signer.sign(data)
    assert signer.verify(sig, data)
    tampered = {"x": 1, "y": [2, 4], "z": {"a": True}}
    assert not signer.verify(sig, tampered)
