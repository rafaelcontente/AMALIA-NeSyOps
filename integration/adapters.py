"""Adaptadores para sistemas externos (dados abertos, legados, etc.)."""
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone
import json

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

class ExternalSystemAdapter:
    """Adaptador base para sistemas externos."""
    
    def __init__(self, system_name: str, base_url: str):
        self.system_name = system_name
        self.base_url = base_url
        self.calls: List[Dict[str, Any]] = []
    
    def fetch_data(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Busca dados do sistema externo.
        
        Em produção, isto faria HTTP GET para o endpoint.
        Aqui simulamos uma resposta.
        """
        # Simular resposta
        response = {
            "system": self.system_name,
            "endpoint": endpoint,
            "params": params or {},
            "data": {"mock": "data"},
            "timestamp": utc_now()
        }
        
        self.calls.append({
            "type": "fetch",
            "endpoint": endpoint,
            "params": params,
            "response": response,
            "timestamp": utc_now()
        })
        
        return response
    
    def post_data(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Envia dados para o sistema externo.
        
        Em produção, isto faria HTTP POST para o endpoint.
        Aqui simulamos uma resposta.
        """
        response = {
            "system": self.system_name,
            "endpoint": endpoint,
            "data_sent": data,
            "status": "success",
            "timestamp": utc_now()
        }
        
        self.calls.append({
            "type": "post",
            "endpoint": endpoint,
            "data": data,
            "response": response,
            "timestamp": utc_now()
        })
        
        return response
    
    def get_call_history(self) -> List[Dict[str, Any]]:
        """Retorna histórico de chamadas ao sistema externo."""
        return self.calls

class OpenDataAdapter(ExternalSystemAdapter):
    """Adaptador para dados abertos (ex: dados.gov.pt)."""
    
    def __init__(self, base_url: str = "https://dados.gov.pt/api"):
        super().__init__("open_data", base_url)
    
    def fetch_dataset(self, dataset_id: str) -> Dict[str, Any]:
        """Busca um dataset específico."""
        return self.fetch_data(f"/datasets/{dataset_id}")

class LegacySystemAdapter(ExternalSystemAdapter):
    """Adaptador para sistemas legados."""
    
    def __init__(self, system_name: str, base_url: str):
        super().__init__(f"legacy_{system_name}", base_url)
    
    def query_legacy(self, query: str) -> Dict[str, Any]:
        """Executa uma query no sistema legado."""
        return self.post_data("/query", {"query": query})

class EntityResolutionAdapter(ExternalSystemAdapter):
    """Adaptador para resolução de entidades e screening."""
    
    def __init__(self, base_url: str = "https://entity-resolution.eu/api"):
        super().__init__("entity_resolution", base_url)
    
    def resolve_entity(self, entity_data: Dict[str, Any]) -> Dict[str, Any]:
        """Resolve uma entidade contra registos oficiais."""
        return self.post_data("/resolve", entity_data)
    
    def screen_sanctions(self, entity_id: str) -> Dict[str, Any]:
        """Verifica se entidade está em listas de sanções."""
        return self.fetch_data(f"/sanctions/{entity_id}")
