"""Security tests: personal data leakage."""
import pytest
from audit.entry import AuditEntry
from audit.ledger import AuditLedger
from audit.privacy import PrivacyManager


class TestDataLeakage:
    def test_pseudonym_generated(self):
        e = AuditEntry(
            trace_id="T-001", model_version="v1", prompt_version="p1",
            rules_version="r1", schema_version="s1",
            input_data={"nome": "Joao Silva", "nif": "123456789", "age": 25},
            decision={"status": "approved"},
        )
        ledger = AuditLedger()
        stored = ledger.append(e)
        assert stored.input_pseudonym is not None
        assert len(stored.input_pseudonym) == 64

    def test_erasure_removes_personal_data(self):
        e = AuditEntry(
            trace_id="T-001", model_version="v1", prompt_version="p1",
            rules_version="r1", schema_version="s1",
            input_data={"nome": "Joao Silva", "nif": "123456789", "age": 25},
            decision={"status": "approved"},
        )
        ledger = AuditLedger()
        ledger.append(e)
        pm = PrivacyManager()
        updated = pm.right_to_erasure(ledger.entries, "T-001")
        assert "_redacted" in updated[0].input_data
        assert "nome" not in updated[0].input_data
