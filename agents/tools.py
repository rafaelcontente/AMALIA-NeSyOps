"""
Sistema de ferramentas com whitelist e auditoria.
Zero Trust: apenas ferramentas na lista de permissões podem ser chamadas.
"""
from typing import Dict, Any, List, Callable
from datetime import datetime, timezone

class ToolRegistry:
    """Registo de ferramentas com whitelist e auditoria."""
    
    def __init__(self, allowed_tools: List[str] = None):
        self.allowed_tools = set(allowed_tools or [])
        self.tools: Dict[str, Callable] = {}
        self.audit_log: List[Dict[str, Any]] = []
    
    def register_tool(self, name: str, func: Callable):
        """Regista uma ferramenta (não implica que esteja na whitelist)."""
        self.tools[name] = func
    
    def call_tool(self, name: str, args: Dict[str, Any], trace_id: str) -> Dict[str, Any]:
        """Chama uma ferramenta se estiver na whitelist. Caso contrário, bloqueia."""
        timestamp = datetime.now(timezone.utc).isoformat()
        
        if name not in self.allowed_tools:
            # Bloquear e registar
            self.audit_log.append({
                "timestamp": timestamp,
                "trace_id": trace_id,
                "tool_name": name,
                "status": "blocked",
                "reason": "not_in_whitelist"
            })
            raise PermissionError(f"Ferramenta '{name}' não está na lista de permissões")
        
        if name not in self.tools:
            self.audit_log.append({
                "timestamp": timestamp,
                "trace_id": trace_id,
                "tool_name": name,
                "status": "error",
                "reason": "tool_not_registered"
            })
            raise ValueError(f"Ferramenta '{name}' não está registada")
        
        # Chamar ferramenta
        try:
            result = self.tools[name](**args)
            self.audit_log.append({
                "timestamp": timestamp,
                "trace_id": trace_id,
                "tool_name": name,
                "status": "success",
                "args": args,
                "result": result
            })
            return result
        except Exception as e:
            self.audit_log.append({
                "timestamp": timestamp,
                "trace_id": trace_id,
                "tool_name": name,
                "status": "error",
                "reason": str(e)
            })
            raise
    
    def get_audit_log(self) -> List[Dict[str, Any]]:
        return self.audit_log
