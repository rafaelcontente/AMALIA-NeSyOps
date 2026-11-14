"""Shared fixtures and global safety guarantees for the test suite."""
import socket
import pytest
from core.models import TraceID, Proposal


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    """Guarantee: the suite never touches the network (no LLM calls, no APIs)."""
    def _blocked(*args, **kwargs):
        raise AssertionError("Test attempted network access; suite must run offline")
    monkeypatch.setattr(socket, "socket", _blocked)
    yield


@pytest.fixture
def trace_id():
    return TraceID()


@pytest.fixture
def sample_proposal(trace_id):
    return Proposal(
        trace_id=trace_id,
        agent="test-agent",
        content={"applicant_age": 25, "business_area": 100, "tax_paid": True},
        confidence=0.95,
    )


@pytest.fixture
def golden_case():
    return {
        "input": {"age": 25, "income": 30000, "household_size": 3, "area_m2": 100},
        "expected_decision": "approved",
        "expected_rules": ["R-001", "R-002", "R-003"],
        "confidence_threshold": 0.85,
    }
