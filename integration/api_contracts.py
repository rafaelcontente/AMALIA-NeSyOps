"""Contratos de API versionados com validação de schemas."""
from typing import Dict, Any, Optional

VALID_STATUSES = {"approved", "rejected", "escalated", "repaired"}
VALID_PRIORITIES = {"low", "normal", "high", "critical"}

SCHEMAS = {
    "v1": {
        "request_required": ["document_text"],
        "request_optional": ["metadata", "priority"],
        "response_required": ["trace_id", "status", "timestamp"],
    },
    "v2": {
        "request_required": ["document_text"],
        "request_optional": ["metadata", "priority", "callback_url", "tags"],
        "response_required": ["trace_id", "status", "timestamp", "confidence"],
    },
}


class APIContractValidator:
    """Valida requests e responses contra schemas versionados."""
    
    def __init__(self, version: str = "v1"):
        if version not in SCHEMAS:
            raise ValueError(f"Unsupported version: {version}")
        self.version = version
        self.schema = SCHEMAS[version]
    
    def validate_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        for field in self.schema["request_required"]:
            if field not in request:
                return {"valid": False, "error": f"Missing required field: {field}"}
        
        normalized = dict(request)
        if "priority" not in normalized:
            normalized["priority"] = "normal"
        elif normalized["priority"] not in VALID_PRIORITIES:
            return {"valid": False, "error": f"Invalid priority: {normalized['priority']}"}
        
        return {"valid": True, "normalized": normalized}
    
    def validate_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        for field in self.schema["response_required"]:
            if field not in response:
                return {"valid": False, "error": f"Missing required field: {field}"}
        
        if response["status"] not in VALID_STATUSES:
            return {"valid": False, "error": f"Invalid status: {response['status']}"}
        
        return {"valid": True}
