"""Sistema de idempotência para evitar processamento duplicado."""
from typing import Dict, Any, Optional
from datetime import datetime, timezone, timedelta
import hashlib
import json

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

class IdempotencyKey:
    """Chave de idempotência baseada em hash do request."""
    
    def __init__(self, request_data: Dict[str, Any], entity_id: str):
        self.entity_id = entity_id
        self.request_hash = self._compute_hash(request_data)
        self.key = f"{entity_id}:{self.request_hash}"
    
    def _compute_hash(self, data: Dict[str, Any]) -> str:
        """Computa hash SHA256 do request."""
        json_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(json_str.encode()).hexdigest()

class IdempotencyStore:
    """Armazena resultados de requests processados."""
    
    def __init__(self, ttl_hours: int = 24):
        self.store: Dict[str, Dict[str, Any]] = {}
        self.ttl = timedelta(hours=ttl_hours)
    
    def get(self, idempotency_key: str) -> Optional[Dict[str, Any]]:
        """Retorna resultado cached se existir e não expirado."""
        if idempotency_key not in self.store:
            return None
        
        record = self.store[idempotency_key]
        if utc_now() > record["expires_at"]:
            # Expirado, remover
            del self.store[idempotency_key]
            return None
        
        return record["result"]
    
    def set(self, idempotency_key: str, result: Dict[str, Any]):
        """Armazena resultado com TTL."""
        self.store[idempotency_key] = {
            "result": result,
            "created_at": utc_now(),
            "expires_at": utc_now() + self.ttl
        }
    
    def cleanup_expired(self):
        """Remove entradas expiradas."""
        now = utc_now()
        expired_keys = [
            key for key, record in self.store.items()
            if now > record["expires_at"]
        ]
        for key in expired_keys:
            del self.store[key]

class IdempotencyManager:
    """Gestor de idempotência para requests."""
    
    def __init__(self, ttl_hours: int = 24):
        self.store = IdempotencyStore(ttl_hours)
    
    def check_and_process(self, request_data: Dict[str, Any], entity_id: str,
                          process_fn) -> Dict[str, Any]:
        """
        Verifica se request já foi processado. Se sim, retorna cached.
        Se não, processa e armazena resultado.
        
        Args:
            request_data: Dados do request
            entity_id: ID da entidade (tenant)
            process_fn: Função que processa o request
        
        Returns:
            Resultado (cached ou novo) com flag "cached"
        """
        # Gerar chave de idempotência
        idem_key = IdempotencyKey(request_data, entity_id)
        
        # Verificar cache
        cached_result = self.store.get(idem_key.key)
        if cached_result is not None:
            return {
                "cached": True,
                "idempotency_key": idem_key.key,
                "result": cached_result
            }
        
        # Processar request
        result = process_fn(request_data, entity_id)
        
        # Armazenar resultado
        self.store.set(idem_key.key, result)
        
        return {
            "cached": False,
            "idempotency_key": idem_key.key,
            "result": result
        }
