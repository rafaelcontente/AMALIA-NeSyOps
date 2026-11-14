"""Shared fixtures for all tests."""
import pytest
from core.models import TraceID, Proposal

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
