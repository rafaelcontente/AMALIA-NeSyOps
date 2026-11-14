"""Unit tests for immutable audit log."""
import pytest
from audit.entry import AuditEntry
from audit.ledger import AuditLedger


def _entry(tid="T-001", age=25):
    return AuditEntry(
        trace_id=tid, model_version="v1", prompt_version="p1",
        rules_version="r1", schema_version="s1",
        input_data={"age": age}, decision={"status": "approved"},
    )


class TestAuditLog:
    def test_hash_computed(self):
        e = _entry()
        h = e.compute_hash()
        assert len(h) == 64

    def test_chain_integrity(self):
        ledger = AuditLedger()
        for i in range(3):
            ledger.append(_entry(tid=f"T-{i}", age=25 + i))
        v = ledger.verify_chain()
        assert v["valid"] is True

    def test_tampering_detected(self):
        ledger = AuditLedger()
        ledger.append(_entry())
        d = ledger.entries[0].model_dump()
        d["input_data"]["age"] = 999
        ledger.entries[0] = AuditEntry(**d)
        v = ledger.verify_chain()
        assert v["valid"] is False
        assert v["broken_at"] == 0
