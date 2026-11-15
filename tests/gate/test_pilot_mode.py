"""Testes do Modo Piloto (Pilot Mode)."""
import os
import pytest
from gate.pilot_mode import PilotModeManager
from review.queue import ReviewQueue
from review.incidents import IncidentManager


@pytest.fixture(autouse=True)
def setup_env():
    os.environ["PILOT_MODE"] = "false"
    yield
    os.environ.pop("PILOT_MODE", None)


@pytest.fixture
def pilot_manager():
    return PilotModeManager(ReviewQueue(), IncidentManager())


def test_pilot_mode_inactive_by_default(pilot_manager):
    assert pilot_manager.is_active is False


def test_pilot_mode_intercept_when_active():
    os.environ["PILOT_MODE"] = "true"
    q = ReviewQueue()
    im = IncidentManager()
    manager = PilotModeManager(q, im)

    decision = {"verdict": {"status": "approved"}, "proposal": {"idade": 25}}
    result = manager.intercept_decision(
        "trace-123", decision, proposal={"idade": 25}, proposer_id="extractor-v1"
    )

    assert result["pilot_status"] == "pending_review"
    assert result["verdict"]["status"] == "pending_review"
    assert q.size() == 1
    assert len(im.get_open_incidents()) == 1


def test_pilot_mode_pass_through_when_inactive(pilot_manager):
    decision = {"verdict": {"status": "approved"}}
    result = pilot_manager.intercept_decision("trace-123", decision)

    assert "pilot_status" not in result
    assert result["verdict"]["status"] == "approved"
