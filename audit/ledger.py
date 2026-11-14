"""
Ledger de auditoria: registo append-only com hash chain.
Suporta verificação de integridade e replay.
"""
from typing import List, Dict, Any, Optional
from audit.entry import AuditEntry
from audit.crypto import compute_sha256, sign_chain, verify_signature, pseudonymize_data
from datetime import datetime, timezone

class AuditLedger:
    """Ledger de auditoria com hash chain."""
    
    def __init__(self):
        self.entries: List[AuditEntry] = []
        self.signatures: List[Dict[str, Any]] = []
    
    def append(self, entry: AuditEntry) -> AuditEntry:
        """
        Adiciona uma entrada ao ledger.
        Calcula o hash chain e armazena.
        """
        # Calcular hash da entrada anterior
        if self.entries:
            previous_hash = self.entries[-1].entry_hash
        else:
            previous_hash = None
        
        # Pseudonimizar dados pessoais se necessário
        input_pseudonym = pseudonymize_data(entry.input_data)
        
        # Criar nova entrada com hash chain
        entry_dict = entry.model_dump()
        entry_dict["previous_hash"] = previous_hash
        entry_dict["input_pseudonym"] = input_pseudonym
        
        # Criar entrada atualizada
        updated_entry = AuditEntry(**entry_dict)
        
        # Calcular hash da entrada
        entry_hash = updated_entry.compute_hash()
        
        # Atualizar com o hash
        final_dict = updated_entry.model_dump()
        final_dict["entry_hash"] = entry_hash
        final_entry = AuditEntry(**final_dict)
        
        self.entries.append(final_entry)
        return final_entry
    
    def verify_chain(self) -> Dict[str, Any]:
        """
        Verifica a integridade da cadeia de hashes.
        Retorna: {"valid": bool, "broken_at": int | None, "message": str}
        """
        if not self.entries:
            return {"valid": True, "broken_at": None, "message": "Ledger vazio"}
        
        for i, entry in enumerate(self.entries):
            # Verificar hash da entrada
            expected_hash = entry.compute_hash()
            if entry.entry_hash != expected_hash:
                return {
                    "valid": False,
                    "broken_at": i,
                    "message": f"Hash inválido no registo {i}: esperado {expected_hash[:16]}..., obtido {entry.entry_hash[:16]}..."
                }
            
            # Verificar hash chain (exceto para a primeira entrada)
            if i > 0:
                if entry.previous_hash != self.entries[i-1].entry_hash:
                    return {
                        "valid": False,
                        "broken_at": i,
                        "message": f"Cadeia quebrada no registo {i}: previous_hash não corresponde"
                    }
        
        return {"valid": True, "broken_at": None, "message": "Cadeia íntegra"}
    
    def get_timeline(self, trace_id: str) -> List[AuditEntry]:
        """Retorna a linha do tempo completa para um trace ID."""
        return [e for e in self.entries if e.trace_id == trace_id]
    
    def sign_periodic(self, private_key: str = "mock-key") -> Dict[str, Any]:
        """Assina periodicamente a cadeia de entradas."""
        if not self.entries:
            return {"signature": "", "entries_count": 0}
        
        entries_dicts = [e.model_dump() for e in self.entries]
        signature = sign_chain(entries_dicts, private_key)
        
        signature_record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "entries_count": len(self.entries),
            "signature": signature
        }
        
        self.signatures.append(signature_record)
        return signature_record
    
    def verify_signature(self, private_key: str = "mock-key") -> bool:
        """Verifica a assinatura mais recente."""
        if not self.signatures:
            return True  # Sem assinaturas, nada a verificar
        
        latest_signature = self.signatures[-1]
        entries_dicts = [e.model_dump() for e in self.entries]
        
        return verify_signature(entries_dicts, latest_signature["signature"], private_key)
