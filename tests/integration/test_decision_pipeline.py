"""Integration tests: full decision pipeline."""
import pytest
from core.models import Proposal, TraceID
from gate.gate import Gate
from gate.validator import GateValidator
from audit.ledger import AuditLedger
from audit.entry import AuditEntry


class TestDecisionPipeline:
    def test_end_to_end(self):
        p = Proposal(
            trace_id=TraceID(), agent="test",
            content={"applicant_age": 25, "business_area": 100, "tax_paid": True},
            confidence=0.95,
        )
        gate = Gate(GateValidator())
        result = gate.evaluate(p)
        ledger = AuditLedger()
        ledger.append(AuditEntry(
            trace_id=str(p.trace_id), model_version="v1", prompt_version="p1",
            rules_version="r1", schema_version="s1",
            input_data=p.content, decision=result["verdict"].model_dump(),
        ))
        assert result["verdict"] is not None
        assert len(ledger.entries) == 1
        assert ledger.verify_chain()["valid"] is True

    def test_validator_failure_rejects(self):
        class Broken(GateValidator):
            def validate(self, proposal, context=None):
                raise RuntimeError("LLM down")
        gate = Gate(Broken())
        p = Proposal(trace_id=TraceID(), agent="t", content={"age": 25}, confidence=0.9)
        result = gate.evaluate(p)
        assert result["verdict"].status == "rejected"
