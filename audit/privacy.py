"""
Gestão de privacidade: retenção, apagamento e pseudonimização (RGPD).
"""
from typing import List, Dict, Any
from audit.entry import AuditEntry
from audit.crypto import pseudonymize_data
from datetime import datetime, timezone

class PrivacyManager:
    """Gestor de privacidade e retenção de dados."""
    
    def __init__(self):
        self.retention_periods = {
            "default": 365 * 5,  # 5 anos por defeito
            "personal_data": 365 * 2,  # 2 anos para dados pessoais
            "audit_logs": 365 * 10  # 10 anos para logs de auditoria
        }
    
    def apply_retention(self, entries: List[AuditEntry]) -> List[AuditEntry]:
        """
        Aplica políticas de retenção.
        Remove dados pessoais de entradas expiradas, mantendo hashes e pseudónimos.
        """
        now = datetime.now(timezone.utc)
        updated_entries = []
        
        for entry in entries:
            # Verificar se a retenção expirou
            if entry.retention_until and entry.retention_until < now:
                # Remover dados pessoais, manter apenas hashes e pseudónimos
                sanitized_dict = entry.model_dump()
                sanitized_dict["input_data"] = {"_redacted": True, "pseudonym": entry.input_pseudonym}
                sanitized_dict["llm_output"] = "[REDACTED - Retenção expirada]"
                
                sanitized_entry = AuditEntry(**sanitized_dict)
                updated_entries.append(sanitized_entry)
            else:
                updated_entries.append(entry)
        
        return updated_entries
    
    def right_to_erasure(self, entries: List[AuditEntry], trace_id: str) -> List[AuditEntry]:
        """
        Direito ao esquecimento (RGPD Artigo 17).
        Remove dados pessoais de um trace específico, mantendo a integridade da cadeia.
        """
        updated_entries = []
        
        for entry in entries:
            if entry.trace_id == trace_id:
                # Pseudonimizar completamente
                sanitized_dict = entry.model_dump()
                sanitized_dict["input_data"] = {"_redacted": True, "pseudonym": entry.input_pseudonym}
                sanitized_dict["llm_output"] = "[REDACTED - Direito ao esquecimento]"
                
                # Recalcular hash para manter a cadeia válida
                sanitized_entry = AuditEntry(**sanitized_dict)
                updated_entries.append(sanitized_entry)
            else:
                updated_entries.append(entry)
        
        return updated_entries
