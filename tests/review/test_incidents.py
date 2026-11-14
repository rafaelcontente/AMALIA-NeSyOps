"""Testes de gestão de incidentes."""
import pytest
from review.incidents import IncidentManager, RUNBOOKS


@pytest.fixture
def incident_manager():
    return IncidentManager()


def test_report_incident(incident_manager):
    incident = incident_manager.report_incident(
        severity="high",
        title="LLM hallucination",
        description="Fictitious entity",
        affected_component="agents/ollama_adapter.py",
    )
    assert incident.status == "open"
    assert incident.severity == "high"


def test_resolve_incident(incident_manager):
    incident = incident_manager.report_incident(
        severity="critical",
        title="Audit chain broken",
        description="Hash mismatch",
        affected_component="audit/ledger.py",
    )
    result = incident_manager.resolve_incident(
        incident.incident_id,
        resolution="Rebuilt chain",
        runbook_followed="audit_chain_broken",
    )
    assert result["status"] == "resolved"


def test_invalid_severity(incident_manager):
    with pytest.raises(ValueError, match="Invalid severity"):
        incident_manager.report_incident("extreme", "Test", "Test", "test")


def test_get_open_incidents(incident_manager):
    incident_manager.report_incident("high", "Incident 1", "Desc", "comp")
    incident_manager.report_incident("medium", "Incident 2", "Desc", "comp")
    i3 = incident_manager.report_incident("low", "Incident 3", "Desc", "comp")
    incident_manager.resolve_incident(i3.incident_id, "Fixed")
    assert len(incident_manager.get_open_incidents()) == 2


def test_get_runbook(incident_manager):
    runbook = incident_manager.get_runbook("kill_switch_activated")
    assert runbook is not None
    assert "steps" in runbook


def test_list_runbooks(incident_manager):
    runbooks = incident_manager.list_runbooks()
    assert "kill_switch_activated" in runbooks
    assert "audit_chain_broken" in runbooks
    assert "llm_hallucination_detected" in runbooks
    assert "circuit_breaker_open" in runbooks


def test_runbooks_are_complete():
    for name, runbook in RUNBOOKS.items():
        assert "title" in runbook
        assert "steps" in runbook
        assert len(runbook["steps"]) >= 3
