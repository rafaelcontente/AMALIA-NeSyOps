"""Testes de autenticação JWT e API keys."""
import pytest
import time
from integration.auth import Authenticator, APIKeyManager

def _make_jwt(payload: dict, secret: str) -> str:
    """Helper para criar JWT válido."""
    import base64, json, hmac, hashlib
    def b64(data): return base64.urlsafe_b64encode(data).rstrip(b"=").decode()
    header = b64(json.dumps({"alg": "HS256"}).encode())
    payload_b64 = b64(json.dumps(payload).encode())
    sig = hmac.new(secret.encode(), f"{header}.{payload_b64}".encode(), hashlib.sha256).digest()
    return f"{header}.{payload_b64}.{b64(sig)}"


def test_jwt_valid_token():
    auth = Authenticator(jwt_secret="my-secret")
    token = _make_jwt({"user_id": "u1", "entity_id": "t1", "exp": time.time() + 3600}, "my-secret")
    result = auth.validate_jwt(token)
    assert result["valid"] is True
    assert result["user_id"] == "u1"
    assert result["entity_id"] == "t1"


def test_jwt_expired_token():
    auth = Authenticator(jwt_secret="my-secret")
    token = _make_jwt({"user_id": "u1", "exp": time.time() - 100}, "my-secret")
    result = auth.validate_jwt(token)
    assert result["valid"] is False
    assert "expired" in result["error"].lower()


def test_jwt_invalid_signature():
    auth = Authenticator(jwt_secret="correct")
    token = _make_jwt({"user_id": "u1", "exp": time.time() + 3600}, "wrong")
    result = auth.validate_jwt(token)
    assert result["valid"] is False
    assert "signature" in result["error"].lower()


def test_jwt_malformed():
    auth = Authenticator(jwt_secret="s")
    assert auth.validate_jwt("not.a.valid.token")["valid"] is False
    assert auth.validate_jwt("garbage")["valid"] is False


def test_api_key_generate_and_validate():
    mgr = APIKeyManager()
    result = mgr.generate_api_key(entity_id="t1", user_id="u1")
    key = result["api_key"]
    
    assert len(key) >= 32
    validation = mgr.validate_api_key(key)
    assert validation["valid"] is True
    assert validation["entity_id"] == "t1"
    assert validation["user_id"] == "u1"


def test_api_key_unknown():
    mgr = APIKeyManager()
    result = mgr.validate_api_key("nonexistent-key")
    assert result["valid"] is False


def test_api_key_revocation():
    mgr = APIKeyManager()
    result = mgr.generate_api_key(entity_id="t1", user_id="u1")
    key = result["api_key"]
    
    mgr.revoke_api_key(key)
    validation = mgr.validate_api_key(key)
    assert validation["valid"] is False
    assert "revoked" in validation["error"].lower()
