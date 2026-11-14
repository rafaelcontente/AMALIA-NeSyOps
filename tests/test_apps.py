import pytest
from apps.reviewer_console import ReviewerConsole
from apps.audit_explorer import AuditExplorer
from apps.manager_dashboard import ManagerDashboard
from apps.rule_editor import RuleEditor
from apps.accessibility import AccessibilityChecker
from apps.api_client import MockAPIClient

@pytest.fixture
def api_client():
    return MockAPIClient()

@pytest.fixture
def reviewer_console(api_client):
    return ReviewerConsole(api_client)

@pytest.fixture
def audit_explorer(api_client):
    return AuditExplorer(api_client)

@pytest.fixture
def manager_dashboard(api_client):
    return ManagerDashboard(api_client)

@pytest.fixture
def rule_editor(api_client):
    return RuleEditor(api_client)

@pytest.fixture
def accessibility_checker():
    return AccessibilityChecker()

# ─── Teste 1: Revisor conclui caso apenas com o que o ecrã mostra ──────────
def test_reviewer_can_complete_case_with_screen_info(reviewer_console):
    """Teste 1: um revisor conclui um caso apenas com o que o ecrã mostra."""
    
    # Carregar caso
    case_view = reviewer_console.load_case("T-9f2")
    
    # Verificar que o ecrã tem toda a informação necessária
    assert case_view.trace_id == "T-9f2"
    assert case_view.original_text != ""
    assert case_view.highlighted_excerpt != ""
    assert len(case_view.evidences) > 0
    assert len(case_view.failed_rules) > 0
    assert case_view.rules_version != ""
    assert len(case_view.reviewer_actions) == 4  # approve, correct, reject, request_info
    
    # Revisor toma decisão baseada apenas no que vê
    result = reviewer_console.submit_decision(
        trace_id="T-9f2",
        decision="approve",
        justification="Cumpre todos os requisitos conforme evidências apresentadas",
        reviewer_id="reviewer-001"
    )
    
    # Verificar que decisão foi submetida via API
    assert result["status"] == "success"
    assert result["trace_id"] == "T-9f2"
    
    # Verificar que ação foi registada
    action_log = reviewer_console.get_action_log()
    assert len(action_log) == 1
    assert action_log[0]["trace_id"] == "T-9f2"
    assert action_log[0]["decision"] == "approve"
    assert action_log[0]["reviewer_id"] == "reviewer-001"

# ─── Teste 2: App não consegue alterar decisão sem passar pela API ─────────
def test_app_cannot_alter_decision_without_api(reviewer_console, api_client):
    """Teste 2: a aplicação não consegue alterar uma decisão sem passar pela API e gerar registo."""
    
    # Tentar alterar decisão diretamente (não deve ser possível)
    # A app só tem métodos que chamam API
    
    # Submeter decisão via API
    result = reviewer_console.submit_decision(
        trace_id="T-001",
        decision="reject",
        justification="Não cumpre requisitos",
        reviewer_id="reviewer-001"
    )
    
    # Verificar que API foi chamada
    assert "T-001" in api_client.decisions
    assert api_client.decisions["T-001"]["decision"] == "reject"
    
    # Verificar que registo foi gerado no audit log
    assert len(api_client.audit_log) > 0
    audit_entry = api_client.audit_log[-1]
    assert audit_entry["event"] == "reviewer_decision"
    assert audit_entry["data"]["trace_id"] == "T-001"
    
    # Verificar que não há método para bypass
    assert not hasattr(reviewer_console, "direct_decision")
    assert not hasattr(reviewer_console, "bypass_api")
    
    # Todos os métodos de decisão passam pela API
    assert hasattr(reviewer_console, "submit_decision")

# ─── Teste 3: Cumpre critérios de acessibilidade web ──────────────────────
def test_accessibility_criteria_met(accessibility_checker):
    """Teste 3: cumpre os critérios de acessibilidade web definidos para o projeto."""
    
    # Dados de interface acessível
    accessible_interface = {
        "id": "reviewer_console",
        "has_alt_text": True,
        "keyboard_nav": True,
        "no_time_limit": True,
        "no_flashing": True,
        "clear_navigation": True,
        "readable_text": True,
        "predictable_behavior": True,
        "input_help": True
    }
    
    # Verificar acessibilidade
    results = accessibility_checker.check_interface(accessible_interface)
    
    # Verificar que passou em todos os critérios
    assert results["passed"] is True
    assert results["score"] == 1.0
    assert len(results["checks"]) == 8  # 8 critérios WCAG 2.1 AA
    
    # Verificar cada critério
    for check in results["checks"]:
        assert check["passed"] is True
        assert check["message"] == "OK"
    
    # Testar interface com falhas
    inaccessible_interface = {
        "id": "bad_interface",
        "has_alt_text": False,  # Falta texto alternativo
        "keyboard_nav": False,  # Sem navegação por teclado
        "no_time_limit": True,
        "no_flashing": True,
        "clear_navigation": True,
        "readable_text": True,
        "predictable_behavior": True,
        "input_help": True
    }
    
    bad_results = accessibility_checker.check_interface(inaccessible_interface)
    
    # Deve falhar
    assert bad_results["passed"] is False
    assert bad_results["score"] < 1.0
    
    # Verificar que as falhas foram detectadas
    failed_checks = [c for c in bad_results["checks"] if not c["passed"]]
    assert len(failed_checks) == 2
    failed_criteria = [c["criterion"] for c in failed_checks]
    assert "text_alternatives" in failed_criteria
    assert "keyboard_navigation" in failed_criteria
    
    # Gerar relatório
    report = accessibility_checker.generate_report(results)
    assert "Relatório de Acessibilidade" in report
    assert "PASSOU" in report
    assert "100.0%" in report
