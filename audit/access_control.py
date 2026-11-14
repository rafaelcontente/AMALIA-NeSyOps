"""Controlo de acesso ao audit ledger."""
from typing import Dict, Set, Optional
from datetime import datetime, timezone


class LedgerAccessControl:
    """
    Controlo de acesso baseado em roles.
    
    Roles:
    - reader: pode ler entradas
    - writer: pode escrever entradas
    - admin: pode ler, escrever e configurar
    """
    
    def __init__(self):
        self.user_roles: Dict[str, Set[str]] = {}
        self.access_log: list = []
    
    def grant_role(self, user_id: str, role: str):
        """Atribui um role a um utilizador."""
        if role not in {"reader", "writer", "admin"}:
            raise ValueError(f"Invalid role: {role}")
        
        if user_id not in self.user_roles:
            self.user_roles[user_id] = set()
        self.user_roles[user_id].add(role)
        
        self._log_access(user_id, f"granted:{role}", success=True)
    
    def revoke_role(self, user_id: str, role: str):
        """Revoga um role de um utilizador."""
        if user_id in self.user_roles:
            self.user_roles[user_id].discard(role)
            self._log_access(user_id, f"revoked:{role}", success=True)
    
    def has_permission(self, user_id: str, permission: str) -> bool:
        """
        Verifica se um utilizador tem uma permissão.
        
        Permissions:
        - read: ler entradas
        - write: escrever entradas
        - admin: operações administrativas
        """
        roles = self.user_roles.get(user_id, set())
        
        if permission == "read":
            return bool(roles & {"reader", "writer", "admin"})
        elif permission == "write":
            return bool(roles & {"writer", "admin"})
        elif permission == "admin":
            return "admin" in roles
        else:
            return False
    
    def check_permission(self, user_id: str, permission: str):
        """
        Verifica permissão e lança exceção se não tiver.
        
        Raises:
            PermissionError: Se o utilizador não tiver a permissão
        """
        if not self.has_permission(user_id, permission):
            self._log_access(user_id, permission, success=False)
            raise PermissionError(
                f"User {user_id} does not have permission: {permission}"
            )
        self._log_access(user_id, permission, success=True)
    
    def _log_access(self, user_id: str, action: str, success: bool):
        """Regista tentativa de acesso."""
        self.access_log.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "user_id": user_id,
            "action": action,
            "success": success,
        })
    
    def get_access_log(self, user_id: Optional[str] = None) -> list:
        """Retorna o log de acessos (opcionalmente filtrado por user_id)."""
        if user_id:
            return [entry for entry in self.access_log if entry["user_id"] == user_id]
        return list(self.access_log)
