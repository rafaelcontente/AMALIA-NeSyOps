"""Invariant: no decision leaves the API without an audit record.

Audit write happens BEFORE the idempotency cache stores the result,
so a failed audit can never be bypassed by a cached retry.
"""
import pytest
from integration.api import APIGateway, DecisionRequest
from integration.idempotency import IdempotencyManager
from integration.tenant import TenantManager
from audit.ledger import AuditLedger
from gate.gate import Gate
from gate.validator import GateValidator


def _gateway(ledger=None):
    tm = TenantManager()
    tm.register_tenant("entity-A", {"name": "A"})
    tm.register_user("user-A", "entity-A", ["read", "write"])
    return APIGateway(Gate(GateValidator()), IdempotencyManager(), tm, ledger=ledger)


def _req(rid, text="Requerimento de licenca comercial"):
    return DecisionRequest(request_id=rid, entity_id="entity-A", user_id="user-A",
                           document_text=text, metadata={})


class TestAuditInvariant:
    def test_every_decision_has_audit_entry(self):
        gw = _gateway()
        for i in range(5):
            r = gw.submit_decision(_req(f"r{i}", text=f"Requerimento numero {i}"))
            assert gw.get_decision(r.trace_id, "user-A") is not None
            assert len(gw.ledger.get_timeline(r.trace_id)) == 1
        assert gw.ledger.verify_chain()["valid"] is True

    def test_all_released_results_have_audit_entries(self):
        gw = _gateway()
        for i in range(5):
            gw.submit_decision(_req(f"r{i}", text=f"Pedido distinto {i}"))
        assert len(gw.results) == 5
        for trace_id in gw.results:
            assert gw.ledger.get_timeline(trace_id), f"{trace_id} released without audit"

    def test_idempotent_replay_no_duplicate_entry(self):
        gw = _gateway()
        r1 = gw.submit_decision(_req("r1"))
        r2 = gw.submit_decision(_req("r1"))
        assert r1.trace_id == r2.trace_id
        assert len(gw.ledger.get_timeline(r1.trace_id)) == 1

    def test_audit_failure_blocks_decision(self):
        class BrokenLedger(AuditLedger):
            def append(self, entry):
                raise IOError("disk full")
        gw = _gateway(ledger=BrokenLedger())
        r = gw.submit_decision(_req("r1"))
        assert gw.get_decision(r.trace_id, "user-A") is None
        assert gw.requests[r.trace_id]["status"] == "failed"
        assert len(gw.ledger.entries) == 0

    def test_retry_after_transient_audit_failure(self):
        """Failed audit must not poison the cache: retry audits and decides."""
        class FlakyLedger(AuditLedger):
            fail_once = True
            def append(self, entry):
                if self.fail_once:
                    self.fail_once = False
                    raise IOError("transient")
                return super().append(entry)
        gw = _gateway(ledger=FlakyLedger())
        r1 = gw.submit_decision(_req("r1"))
        assert gw.get_decision(r1.trace_id, "user-A") is None
        r2 = gw.submit_decision(_req("r1"))
        assert gw.get_decision(r2.trace_id, "user-A") is not None
        assert len(gw.ledger.get_timeline(r2.trace_id)) == 1
