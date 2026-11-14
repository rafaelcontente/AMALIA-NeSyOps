"""Segurança para MCP server: validação de inputs e audit logging."""
import re
from typing import Dict, Any, List
from datetime import datetime, timezone

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

# Patterns maliciosos
SQL_INJECTION = re.compile(r"(DROP|DELETE|INSERT|UPDATE|UNION|SELECT).*(FROM|TABLE|INTO|WHERE|SET)", re.IGNORECASE)
PATH_TRAVERSAL = re.compile(r"\.\.[/\\]")
COMMAND_INJECTION = re.compile(r"[;&|`]|rm\s+|echo\s+|'\s*;\s*")


class MCPInputValidator:
    """Valida e sanitiza inputs para MCP tools."""
    
    def validate_and_sanitize(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        sanitized = {}
        for key, value in input_data.items():
            if isinstance(value, str):
                # Detectar ataques claros
                if SQL_INJECTION.search(value) and ("DROP" in value.upper() or ";" in value):
                    return {"valid": False, "error": "Malicious SQL injection detected"}
                if PATH_TRAVERSAL.search(value):
                    return {"valid": False, "error": "Malicious path traversal detected"}
                if COMMAND_INJECTION.search(value):
                    return {"valid": False, "error": "Malicious command injection detected"}
                
                # Sanitizar: remover SQL keywords perigosas
                clean = value
                for kw in ["DROP TABLE", "; DROP", "--"]:
                    clean = re.sub(re.escape(kw), "", clean, flags=re.IGNORECASE)
                clean = re.sub(r"\.\.[/\\]", "", clean)
                sanitized[key] = clean.strip()
            else:
                sanitized[key] = value
        
        return {"valid": True, "sanitized": sanitized}


class MCPSecurityLogger:
    """Audit log para chamadas a MCP tools."""
    
    def __init__(self):
        self.logs: List[Dict[str, Any]] = []
    
    def log_tool_call(
        self,
        tool_name: str,
        entity_id: str,
        user_id: str,
        arguments: Dict[str, Any],
        success: bool,
        error: str = None,
    ):
        entry = {
            "timestamp": utc_now().isoformat(),
            "tool_name": tool_name,
            "entity_id": entity_id,
            "user_id": user_id,
            "arguments": arguments,
            "success": success,
        }
        if error:
            entry["error"] = error
        self.logs.append(entry)
    
    def get_audit_logs(self, entity_id: str = None) -> List[Dict[str, Any]]:
        if entity_id:
            return [l for l in self.logs if l["entity_id"] == entity_id]
        return list(self.logs)
