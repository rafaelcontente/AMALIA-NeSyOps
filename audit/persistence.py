"""Persistência durável para o audit ledger usando SQLite append-only."""
import sqlite3
import json
import threading
from typing import List, Optional, Dict, Any
from pathlib import Path
from datetime import datetime, timezone
from .entry import AuditEntry


class LedgerStorage:
    """Interface abstrata para storage de audit entries."""
    
    def write(self, entry: AuditEntry) -> None:
        raise NotImplementedError
    
    def read_all(self) -> List[AuditEntry]:
        raise NotImplementedError
    
    def read_by_trace(self, trace_id: str) -> List[AuditEntry]:
        raise NotImplementedError
    
    def count(self) -> int:
        raise NotImplementedError


class SQLiteLedgerStorage(LedgerStorage):
    """
    Storage SQLite append-only para audit entries.
    
    Garantias:
    - Append-only: nunca atualiza ou apaga entradas
    - Thread-safe: usa lock para operações concorrentes
    - Durable: usa WAL mode e sync síncrono
    """
    
    def __init__(self, db_path: str = "audit_ledger.db"):
        self.db_path = db_path
        self._lock = threading.Lock()
        self._init_db()
    
    def _init_db(self):
        """Inicializa a base de dados com schema append-only."""
        with self._lock:
            conn = sqlite3.connect(self.db_path)
            # WAL mode para melhor concorrência
            conn.execute("PRAGMA journal_mode=WAL")
            # Synchronous FULL para durabilidade
            conn.execute("PRAGMA synchronous=FULL")
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS audit_entries (
                    id TEXT PRIMARY KEY,
                    trace_id TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    entry_hash TEXT NOT NULL,
                    previous_hash TEXT,
                    data_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
            """)
            
            # Índice para queries por trace_id
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_trace_id 
                ON audit_entries(trace_id)
            """)
            
            conn.commit()
            conn.close()
    
    def write(self, entry: AuditEntry) -> None:
        """
        Escreve uma entrada no ledger (append-only).
        
        Thread-safe e durável.
        """
        with self._lock:
            conn = sqlite3.connect(self.db_path)
            try:
                conn.execute("""
                    INSERT INTO audit_entries 
                    (id, trace_id, timestamp, entry_hash, previous_hash, data_json, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    entry.id,
                    entry.trace_id,
                    entry.timestamp.isoformat(),
                    entry.entry_hash,
                    entry.previous_hash,
                    entry.model_dump_json(),
                    datetime.now(timezone.utc).isoformat()
                ))
                conn.commit()
            finally:
                conn.close()
    
    def read_all(self) -> List[AuditEntry]:
        """Lê todas as entradas ordenadas por timestamp."""
        with self._lock:
            conn = sqlite3.connect(self.db_path)
            try:
                cursor = conn.execute("""
                    SELECT data_json FROM audit_entries 
                    ORDER BY timestamp ASC
                """)
                entries = []
                for row in cursor:
                    data_json = row[0]
                    entry = AuditEntry.model_validate_json(data_json)
                    entries.append(entry)
                return entries
            finally:
                conn.close()
    
    def read_by_trace(self, trace_id: str) -> List[AuditEntry]:
        """Lê todas as entradas para um trace_id específico."""
        with self._lock:
            conn = sqlite3.connect(self.db_path)
            try:
                cursor = conn.execute("""
                    SELECT data_json FROM audit_entries 
                    WHERE trace_id = ?
                    ORDER BY timestamp ASC
                """, (trace_id,))
                entries = []
                for row in cursor:
                    data_json = row[0]
                    entry = AuditEntry.model_validate_json(data_json)
                    entries.append(entry)
                return entries
            finally:
                conn.close()
    
    def count(self) -> int:
        """Retorna o número total de entradas."""
        with self._lock:
            conn = sqlite3.connect(self.db_path)
            try:
                cursor = conn.execute("SELECT COUNT(*) FROM audit_entries")
                return cursor.fetchone()[0]
            finally:
                conn.close()
    
    def delete_db(self):
        """Apaga a base de dados (apenas para testes)."""
        with self._lock:
            if Path(self.db_path).exists():
                Path(self.db_path).unlink()
