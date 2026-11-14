"""Testes do workflow maker-checker."""
import pytest
from review.maker_checker import MakerCheckerPolicy


@pytest.fixture
def policy():
    return MakerCheckerPolicy(required_approvals=2)


def test_single_vote_pending(policy):
    result = policy.submit_vote("case-1", "reviewer-1", "approved", "Looks good")
    assert result["status"] == "pending"
    assert len(result["votes"]) == 1


def test_two_approvals_required(policy):
    policy.submit_vote("case-1", "reviewer-1", "approved")
    result = policy.submit_vote("case-1", "reviewer-2", "approved", "Confirmed")
    assert result["status"] == "approved"
    assert len(result["votes"]) == 2


def test_veto_rejects_immediately(policy):
    policy.submit_vote("case-1", "reviewer-1", "approved")
    result = policy.submit_vote("case-1", "reviewer-2", "rejected", "Safety concern")
    assert result["status"] == "rejected"


def test_duplicate_vote_rejected(policy):
    policy.submit_vote("case-1", "reviewer-1", "approved")
    result = policy.submit_vote("case-1", "reviewer-1", "approved")
    assert result["status"] == "error"
    assert "already voted" in result["error"]


def test_invalid_decision_raises(policy):
    with pytest.raises(ValueError, match="Invalid decision"):
        policy.submit_vote("case-1", "reviewer-1", "maybe")


def test_get_status(policy):
    policy.submit_vote("case-1", "reviewer-1", "approved")
    status = policy.get_status("case-1")
    assert status["status"] == "pending"
    assert status["approvals"] == 1
    assert status["required"] == 2


def test_reset_case(policy):
    policy.submit_vote("case-1", "reviewer-1", "approved")
    policy.reset("case-1")
    status = policy.get_status("case-1")
    assert status["approvals"] == 0


def test_escalation_vote(policy):
    policy.submit_vote("case-1", "reviewer-1", "escalated")
    policy.submit_vote("case-1", "reviewer-2", "escalated")
    status = policy.get_status("case-1")
    assert status["status"] == "pending"
    assert status["approvals"] == 0
