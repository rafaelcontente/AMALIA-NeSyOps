"""Fixtures partilhados para testes de auditoria."""
import pytest
from datetime import datetime, timezone, timedelta
from audit.entry import AuditEntry


@pytest.fixture
def _entry():
    """Factory para criar AuditEntry com todos os campos obrigatórios."""
    def make(**overrides):
        defaults = {
            "trace_id": "trace-test",
            "timestamp": datetime.now(timezone.utc),
            "model_version": "v1.0",
            "prompt_version": "p1.0",
            "rules_version": "r1.0",
            "schema_version": "s1.0",
            "input_data": {"test": True},
            "decision": {"status": "approved"},
        }
        defaults.update(overrides)
        return AuditEntry(**defaults)
    return make
