"""Verificação periódica de integridade do ledger."""
from typing import Dict, Any, List
from datetime import datetime, timezone
from .entry import AuditEntry


class IntegrityChecker:
    """
    Verifica a integridade do ledger periodicamente.
    
    Verificações:
    - Hash chain: cada entry_hash está correto
    - Sequência: previous_hash liga as entradas
    - Duplicados: não há IDs duplicados
    """
    
    def verify_integrity(self, entries: List[AuditEntry]) -> Dict[str, Any]:
        """
        Verifica a integridade completa do ledger.
        
        Retorna relatório com status e detalhes de falhas.
        """
        issues = []
        
        # 1. Verificar duplicados
        seen_ids = set()
        for entry in entries:
            if entry.id in seen_ids:
                issues.append({
                    "type": "duplicate_id",
                    "entry_id": entry.id,
                    "description": f"Duplicate entry ID: {entry.id}"
                })
            seen_ids.add(entry.id)
        
        # 2. Verificar hash chain
        for i, entry in enumerate(entries):
            # Verificar entry_hash
            computed_hash = entry.compute_hash()
            if computed_hash != entry.entry_hash:
                issues.append({
                    "type": "hash_mismatch",
                    "entry_id": entry.id,
                    "expected": entry.entry_hash,
                    "computed": computed_hash,
                    "description": f"Entry hash mismatch at position {i}"
                })
            
            # Verificar previous_hash (exceto para a primeira entrada)
            if i > 0:
                prev_entry = entries[i - 1]
                if entry.previous_hash != prev_entry.entry_hash:
                    issues.append({
                        "type": "chain_break",
                        "entry_id": entry.id,
                        "expected_previous": prev_entry.entry_hash,
                        "actual_previous": entry.previous_hash,
                        "description": f"Chain break at position {i}"
                    })
        
        # 3. Verificar timestamps (devem ser monotónicos)
        for i in range(1, len(entries)):
            if entries[i].timestamp < entries[i - 1].timestamp:
                issues.append({
                    "type": "timestamp_order",
                    "entry_id": entries[i].id,
                    "description": f"Timestamp not monotonic at position {i}"
                })
        
        return {
            "verified_at": datetime.now(timezone.utc).isoformat(),
            "entry_count": len(entries),
            "valid": len(issues) == 0,
            "issues": issues,
            "issue_count": len(issues),
        }
    
    def quick_check(self, entries: List[AuditEntry]) -> bool:
        """
        Verificação rápida: apenas hash chain.
        
        Retorna True se válido, False se houver problemas.
        """
        result = self.verify_integrity(entries)
        return result["valid"]
