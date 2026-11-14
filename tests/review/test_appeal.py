"""Testes do processo de recurso."""
import pytest
from review.appeal import AppealProcess


@pytest.fixture
def appeal_process():
    return AppealProcess()


def test_submit_appeal(appeal_process):
    appeal = appeal_process.submit_appeal(
        original_trace_id="trace-123",
        citizen_id="citizen-456",
        reason="Decisão incorreta",
        supporting_evidence="doc.pdf",
    )
    assert appeal.status == "pending"
    assert appeal.original_trace_id == "trace-123"


def test_review_appeal_approved(appeal_process):
    appeal = appeal_process.submit_appeal("trace-123", "citizen-456", "Reason")
    result = appeal_process.review_appeal(appeal.appeal_id, "reviewer-1", "approved", "Valid")
    assert result["status"] == "approved"
    assert result["new_trace_id"].startswith("APPEAL-")


def test_review_appeal_rejected(appeal_process):
    appeal = appeal_process.submit_appeal("trace-123", "citizen-456", "Reason")
    result = appeal_process.review_appeal(appeal.appeal_id, "reviewer-1", "rejected", "Invalid")
    assert result["status"] == "rejected"


def test_cannot_review_twice(appeal_process):
    appeal = appeal_process.submit_appeal("trace-123", "citizen-456", "Reason")
    appeal_process.review_appeal(appeal.appeal_id, "reviewer-1", "approved")
    result = appeal_process.review_appeal(appeal.appeal_id, "reviewer-2", "rejected")
    assert result["status"] == "error"


def test_get_appeals_by_citizen(appeal_process):
    appeal_process.submit_appeal("trace-1", "citizen-1", "R1")
    appeal_process.submit_appeal("trace-2", "citizen-1", "R2")
    appeal_process.submit_appeal("trace-3", "citizen-2", "R3")
    assert len(appeal_process.get_appeals_by_citizen("citizen-1")) == 2


def test_get_appeals_by_status(appeal_process):
    a1 = appeal_process.submit_appeal("trace-1", "citizen-1", "R1")
    appeal_process.submit_appeal("trace-2", "citizen-2", "R2")
    appeal_process.review_appeal(a1.appeal_id, "reviewer-1", "approved")
    assert len(appeal_process.get_appeals_by_status("pending")) == 1
    assert len(appeal_process.get_appeals_by_status("approved")) == 1


def test_appeal_not_found(appeal_process):
    with pytest.raises(ValueError, match="not found"):
        appeal_process.review_appeal("nonexistent", "reviewer-1", "approved")
