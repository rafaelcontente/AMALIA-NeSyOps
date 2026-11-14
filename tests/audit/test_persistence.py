"""Testes de persistência SQLite append-only."""
import pytest
import tempfile
import threading
import time
from pathlib import Path
from audit.persistence import SQLiteLedgerStorage
from datetime import datetime, timezone


@pytest.fixture
def temp_db():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = str(Path(tmpdir) / "test_ledger.db")
        storage = SQLiteLedgerStorage(db_path)
        yield storage


def test_write_and_read_single_entry(temp_db, _entry):
    entry = _entry(trace_id="trace-1", entry_hash="abc123")
    temp_db.write(entry)
    entries = temp_db.read_all()
    assert len(entries) == 1
    assert entries[0].trace_id == "trace-1"
    assert entries[0].entry_hash == "abc123"


def test_append_only_semantics(temp_db, _entry):
    entry1 = _entry(id="entry-1", trace_id="trace-1", entry_hash="hash1")
    temp_db.write(entry1)
    assert temp_db.count() == 1
    entry_dup = _entry(id="entry-1", trace_id="trace-1", entry_hash="hash1_mod")
    with pytest.raises(Exception):
        temp_db.write(entry_dup)
    assert temp_db.count() == 1


def test_read_by_trace_id(temp_db, _entry):
    for i in range(3):
        temp_db.write(_entry(trace_id="trace-1", entry_hash=f"h{i}"))
    for i in range(2):
        temp_db.write(_entry(trace_id="trace-2", entry_hash=f"h{i}"))
    assert len(temp_db.read_by_trace("trace-1")) == 3
    assert len(temp_db.read_by_trace("trace-2")) == 2
    assert len(temp_db.read_by_trace("trace-3")) == 0


def test_concurrent_writes(temp_db, _entry):
    def write_entry(thread_id):
        entry = _entry(trace_id=f"trace-{thread_id}", entry_hash=f"h{thread_id}")
        temp_db.write(entry)
    threads = [threading.Thread(target=write_entry, args=(i,)) for i in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert temp_db.count() == 10
    entries = temp_db.read_all()
    assert len(set(e.trace_id for e in entries)) == 10


def test_persistence_across_restarts(_entry):
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = str(Path(tmpdir) / "test_ledger.db")
        s1 = SQLiteLedgerStorage(db_path)
        for i in range(5):
            s1.write(_entry(trace_id=f"trace-{i}", entry_hash=f"h{i}"))
        assert s1.count() == 5
        s2 = SQLiteLedgerStorage(db_path)
        assert s2.count() == 5
        for i in range(5, 8):
            s2.write(_entry(trace_id=f"trace-{i}", entry_hash=f"h{i}"))
        assert s2.count() == 8
        s3 = SQLiteLedgerStorage(db_path)
        assert s3.count() == 8


def test_ordering_by_timestamp(temp_db, _entry):
    for i in range(5):
        ts = datetime.now(timezone.utc)
        temp_db.write(_entry(trace_id=f"trace-{i}", timestamp=ts, entry_hash=f"h{i}"))
        time.sleep(0.01)
    entries = temp_db.read_all()
    for i in range(1, len(entries)):
        assert entries[i].timestamp >= entries[i - 1].timestamp
