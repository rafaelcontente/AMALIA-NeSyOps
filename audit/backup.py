"""Backup e restore do audit ledger com verificação de integridade."""
import json
from typing import List, Dict, Any
from pathlib import Path
from datetime import datetime, timezone
from .entry import AuditEntry
from .crypto import compute_sha256


class LedgerBackup:
    """
    Exporta e importa o ledger com verificação de integridade.
    
    Formato de backup:
    {
        "version": "1.0",
        "exported_at": "2026-01-15T10:00:00Z",
        "entry_count": 100,
        "entries": [...],
        "checksum": "sha256:abc123..."
    }
    """
    
    def export_to_file(self, entries: List[AuditEntry], output_path: str) -> Dict[str, Any]:
        """
        Exporta entradas para ficheiro JSON com checksum.
        
        Retorna metadata do backup.
        """
        entries_data = [entry.model_dump(mode="json") for entry in entries]
        
        # Calcular checksum dos dados
        entries_json = json.dumps(entries_data, sort_keys=True)
        checksum = f"sha256:{compute_sha256(entries_json)}"
        
        backup_data = {
            "version": "1.0",
            "exported_at": datetime.now(timezone.utc).isoformat(),
            "entry_count": len(entries),
            "entries": entries_data,
            "checksum": checksum,
        }
        
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(backup_data, f, indent=2, ensure_ascii=False)
        
        return {
            "path": output_path,
            "entry_count": len(entries),
            "checksum": checksum,
            "exported_at": backup_data["exported_at"],
        }
    
    def import_from_file(self, input_path: str) -> List[AuditEntry]:
        """
        Importa entradas de ficheiro JSON com verificação de integridade.
        
        Raises:
            ValueError: Se o checksum não bater
        """
        with open(input_path, "r", encoding="utf-8") as f:
            backup_data = json.load(f)
        
        # Verificar checksum
        entries_data = backup_data["entries"]
        entries_json = json.dumps(entries_data, sort_keys=True)
        expected_checksum = f"sha256:{compute_sha256(entries_json)}"
        
        if expected_checksum != backup_data["checksum"]:
            raise ValueError(
                f"Checksum mismatch: expected {backup_data['checksum']}, "
                f"got {expected_checksum}"
            )
        
        # Reconstruir entradas
        entries = []
        for entry_data in entries_data:
            entry = AuditEntry.model_validate(entry_data)
            entries.append(entry)
        
        return entries
    
    def verify_backup(self, input_path: str) -> bool:
        """Verifica a integridade de um ficheiro de backup."""
        try:
            with open(input_path, "r", encoding="utf-8") as f:
                backup_data = json.load(f)
            
            entries_data = backup_data["entries"]
            entries_json = json.dumps(entries_data, sort_keys=True)
            expected_checksum = f"sha256:{compute_sha256(entries_json)}"
            
            return expected_checksum == backup_data["checksum"]
        except Exception:
            return False
