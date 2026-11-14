"""Unit tests for the 5-layer gate (spec: repair with limit, then escalate)."""
import pytest
from gate.gate import Gate
from gate.validator import GateValidator
from core.models import Proposal, TraceID, VerdictStatus


class TestGuardrails:
    def test_valid_proposal_passes(self, sample_proposal):
        gate = Gate(GateValidator())
        result = gate.evaluate(sample_proposal)
        assert result["verdict"].status in [VerdictStatus.APPROVED, VerdictStatus.ESCALATED]

    def test_empty_content_rejected(self):
        gate = Gate(GateValidator())
        p = Proposal(trace_id=TraceID(), agent="t", content={}, confidence=0.5)
        result = gate.evaluate(p)
        assert result["verdict"].status == VerdictStatus.REJECTED

    def test_inconsistent_dates_blocked_then_escalated(self):
        """Spec: consistency failure -> repair (attempt 1 of 2); exhausted -> escalate."""
        gate = Gate(GateValidator())
        p = Proposal(
            trace_id=TraceID(), agent="t",
            content={"data_inicio": "2026-01-01", "data_fim": "2025-12-31"},
            confidence=0.9,
        )
        r1 = gate.evaluate(p)
        assert r1["verdict"].status != VerdictStatus.APPROVED
        assert r1["verdict"].status == VerdictStatus.REPAIRED
        assert r1["plan"]["action"] == "repair"
        assert r1["plan"]["attempt"] == 1

        r2 = gate.evaluate(p, repair_attempt=2)
        assert r2["verdict"].status == VerdictStatus.ESCALATED
        assert r2["needs_human_approval"] is True

    def test_low_confidence_not_approved(self):
        gate = Gate(GateValidator())
        p = Proposal(trace_id=TraceID(), agent="t", content={"v": 1}, confidence=0.1)
        result = gate.evaluate(p)
        assert result["verdict"].status != VerdictStatus.APPROVED

    def test_unverified_claims_repair_cycle_then_escalate(self):
        """Spec example: 'prazo de 30 dias' sem fonte -> repair 1/2; falhar de novo -> escalar."""
        gate = Gate(GateValidator())
        p = Proposal(trace_id=TraceID(), agent="t", content={"prazo": "30 dias"}, confidence=0.9)
        ctx = {
            "claims_to_verify": [{"text": "prazo", "source_id": "EV-X", "requires_evidence": True}],
            "available_evidences": [],
        }
        r1 = gate.evaluate(p, ctx)
        assert r1["verdict"].status == VerdictStatus.REPAIRED
        assert r1["plan"]["action"] == "repair"
        assert "claims" in r1["verdict"].rules_violated

        r2 = gate.evaluate(p, ctx, repair_attempt=2)
        assert r2["verdict"].status == VerdictStatus.ESCALATED
        assert r2["needs_human_approval"] is True
