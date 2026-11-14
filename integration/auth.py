"""Autenticação JWT e API keys."""
import hmac
import hashlib
import secrets
import time
from typing import Dict, Any, Optional
from datetime import datetime, timezone

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

class Authenticator:
    """Validação de JWT simplificada (HMAC-SHA256)."""
    
    def __init__(self, jwt_secret: str = "default-secret"):
        self.secret = jwt_secret
    
    def _base64url_encode(self, data: bytes) -> str:
        import base64
        return base64.urlsafe_b64encode(data).rstrip(b"=").decode()
    
    def _base64url_decode(self, s: str) -> bytes:
        import base64
        padding = "=" * (4 - len(s) % 4)
        return base64.urlsafe_b64decode(s + padding)
    
    def validate_jwt(self, token: str) -> Dict[str, Any]:
        try:
            parts = token.split(".")
            if len(parts) != 3:
                return {"valid": False, "error": "Invalid token format"}
            
            header_b64, payload_b64, signature_b64 = parts
            
            # Verificar assinatura
            message = f"{header_b64}.{payload_b64}".encode()
            expected_sig = hmac.new(self.secret.encode(), message, hashlib.sha256).digest()
            actual_sig = self._base64url_decode(signature_b64)
            
            if not hmac.compare_digest(expected_sig, actual_sig):
                return {"valid": False, "error": "Invalid signature"}
            
            # Descodificar payload
            import json
            payload = json.loads(self._base64url_decode(payload_b64))
            
            # Verificar expiração
            if "exp" in payload and payload["exp"] < time.time():
                return {"valid": False, "error": "Token expired"}
            
            return {
                "valid": True,
                "user_id": payload.get("user_id"),
                "entity_id": payload.get("entity_id"),
                "payload": payload,
            }
        except Exception as e:
            return {"valid": False, "error": str(e)}


class APIKeyManager:
    """Gestão de API keys com revogação."""
    
    def __init__(self):
        self.keys: Dict[str, Dict[str, Any]] = {}  # api_key -> metadata
        self.revoked: set = set()
    
    def generate_api_key(self, entity_id: str, user_id: str) -> Dict[str, Any]:
        api_key = secrets.token_urlsafe(32)
        self.keys[api_key] = {
            "entity_id": entity_id,
            "user_id": user_id,
            "created_at": utc_now().isoformat(),
        }
        return {
            "api_key": api_key,
            "entity_id": entity_id,
            "user_id": user_id,
        }
    
    def validate_api_key(self, api_key: str) -> Dict[str, Any]:
        if api_key in self.revoked:
            return {"valid": False, "error": "API key revoked"}
        if api_key not in self.keys:
            return {"valid": False, "error": "API key not found"}
        metadata = self.keys[api_key]
        return {
            "valid": True,
            "entity_id": metadata["entity_id"],
            "user_id": metadata["user_id"],
        }
    
    def revoke_api_key(self, api_key: str):
        self.revoked.add(api_key)
