"""Isolamento multi-tenant para garantir que entidades não acedem a dados de outras."""
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

class TenantContext:
    """Contexto de tenant para isolamento de dados."""
    
    def __init__(self, entity_id: str, user_id: str, permissions: List[str] = None):
        self.entity_id = entity_id
        self.user_id = user_id
        self.permissions = permissions or []
        self.created_at = utc_now()
    
    def has_permission(self, permission: str) -> bool:
        """Verifica se o utilizador tem uma permissão específica."""
        return permission in self.permissions

class TenantIsolator:
    """Isolador de dados por tenant."""
    
    def __init__(self):
        self.tenant_data: Dict[str, Dict[str, Any]] = {}
    
    def store_data(self, entity_id: str, data_key: str, data: Dict[str, Any]):
        """Armazena dados para um tenant específico."""
        if entity_id not in self.tenant_data:
            self.tenant_data[entity_id] = {}
        
        self.tenant_data[entity_id][data_key] = {
            "data": data,
            "created_at": utc_now()
        }
    
    def get_data(self, entity_id: str, data_key: str,
                 requesting_entity_id: str) -> Optional[Dict[str, Any]]:
        """
        Retorna dados apenas se o requesting_entity_id corresponder ao entity_id.
        
        Args:
            entity_id: ID do tenant proprietário dos dados
            data_key: Chave dos dados
            requesting_entity_id: ID do tenant que está a pedir os dados
        
        Returns:
            Dados se autorizado, None se não autorizado ou não encontrado
        """
        # Verificar isolamento
        if entity_id != requesting_entity_id:
            raise PermissionError(
                f"Tenant {requesting_entity_id} não pode aceder a dados de {entity_id}"
            )
        
        if entity_id not in self.tenant_data:
            return None
        
        if data_key not in self.tenant_data[entity_id]:
            return None
        
        return self.tenant_data[entity_id][data_key]["data"]
    
    def list_data(self, entity_id: str, requesting_entity_id: str) -> List[str]:
        """Lista todas as chaves de dados de um tenant."""
        if entity_id != requesting_entity_id:
            raise PermissionError(
                f"Tenant {requesting_entity_id} não pode listar dados de {entity_id}"
            )
        
        if entity_id not in self.tenant_data:
            return []
        
        return list(self.tenant_data[entity_id].keys())

class TenantManager:
    """Gestor de tenants e permissões."""
    
    def __init__(self):
        self.tenants: Dict[str, Dict[str, Any]] = {}
        self.users: Dict[str, TenantContext] = {}
    
    def register_tenant(self, entity_id: str, metadata: Dict[str, Any]):
        """Regista um novo tenant."""
        self.tenants[entity_id] = {
            "entity_id": entity_id,
            "metadata": metadata,
            "created_at": utc_now()
        }
    
    def register_user(self, user_id: str, entity_id: str, permissions: List[str]):
        """Regista um utilizador associado a um tenant."""
        if entity_id not in self.tenants:
            raise ValueError(f"Tenant {entity_id} não existe")
        
        self.users[user_id] = TenantContext(
            entity_id=entity_id,
            user_id=user_id,
            permissions=permissions
        )
    
    def get_user_context(self, user_id: str) -> Optional[TenantContext]:
        """Retorna contexto de tenant para um utilizador."""
        return self.users.get(user_id)
    
    def verify_access(self, user_id: str, target_entity_id: str) -> bool:
        """Verifica se utilizador pode aceder a um tenant."""
        context = self.get_user_context(user_id)
        if context is None:
            return False
        
        return context.entity_id == target_entity_id
