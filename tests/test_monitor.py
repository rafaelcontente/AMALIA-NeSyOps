import pytest
import numpy as np
from datetime import datetime, timezone
from monitor.detector import DriftDetector
from monitor.kill_switch import KillSwitch, SafeMode
from monitor.shadow import ShadowDeployer
from monitor.alerts import AlertManager, AlertSeverity

@pytest.fixture
def drift_detector():
    return DriftDetector(psi_threshold=0.2, cosine_threshold=0.1)

@pytest.fixture
def kill_switch():
    return KillSwitch()

@pytest.fixture
def shadow_deployer():
    return ShadowDeployer(active_version="v1.0.0")

@pytest.fixture
def alert_manager():
    return AlertManager(cooldown_minutes=60)

# ─── Teste 1: Drift injetado dispara alerta ─────────────────────────────────
def test_drift_detection_triggers_alert(drift_detector, alert_manager):
    """Teste 1: um drift injetado num dataset de teste dispara alerta dentro do prazo."""
    
    # Baseline: distribuição normal (idade entre 20-60)
    np.random.seed(42)
    baseline_data = {
        "idade": np.random.normal(40, 10, 1000).tolist(),
        "rendimento": np.random.normal(30000, 5000, 1000).tolist()
    }
    
    # Current data sem drift
    current_no_drift = {
        "idade": np.random.normal(40, 10, 500).tolist(),
        "rendimento": np.random.normal(30000, 5000, 500).tolist()
    }
    
    # Current data COM drift (idade mudou significativamente)
    current_with_drift = {
        "idade": np.random.normal(25, 8, 500).tolist(),  # Idade muito mais baixa
        "rendimento": np.random.normal(30000, 5000, 500).tolist()
    }
    
    # Teste 1a: Sem drift não deve detetar nada
    reports_no_drift = drift_detector.detect_tabular_drift(current_no_drift, baseline_data)
    drift_detected_no = any(r.detected for r in reports_no_drift)
    assert not drift_detected_no, "Não deve detetar drift em dados similares"
    
    # Teste 1b: Com drift deve detetar
    reports_with_drift = drift_detector.detect_tabular_drift(current_with_drift, baseline_data)
    idade_report = next(r for r in reports_with_drift if r.feature == "idade")
    
    assert idade_report.detected is True, "Deve detetar drift na idade"
    assert idade_report.drift_score > drift_detector.psi_threshold
    
    # Teste 1c: Levantar alerta baseado no drift detetado
    alert = alert_manager.raise_alert(
        alert_id="drift-idade",
        severity=AlertSeverity.WARNING,
        message=f"Drift detetado na feature 'idade': PSI={idade_report.drift_score:.3f}",
        source="drift_detector",
        details=idade_report.to_dict(),
        force=True
    )
    
    assert alert is not None
    assert alert.severity == AlertSeverity.WARNING
    assert "idade" in alert.message
    
    # Verificar que o alerta está ativo
    active_alerts = alert_manager.get_active_alerts()
    assert len(active_alerts) >= 1
    assert any(a.alert_id == "drift-idade" for a in active_alerts)

# ─── Teste 2: Kill switch ativo → 100% modo seguro ──────────────────────────
def test_kill_switch_forces_safe_mode(kill_switch):
    """Teste 2: com o kill switch ativo, 100% dos novos pedidos vão para modo seguro."""
    
    # Estado inicial: inativo
    assert kill_switch.active is False
    result_normal = kill_switch.process_request({"action": "decide"})
    assert result_normal["mode"] == "normal"
    assert result_normal["action"] == "process"
    
    # Ativar kill switch
    activation = kill_switch.activate(
        reason="Salto anómalo na taxa de violações de R-012",
        activated_by="ops-admin",
        mode=SafeMode.ESCALATE
    )
    assert activation["status"] == "activated"
    assert kill_switch.active is True
    
    # Testar 100 pedidos — TODOS devem ir para modo seguro
    safe_count = 0
    normal_count = 0
    
    for i in range(100):
        result = kill_switch.process_request({"id": i, "action": "decide"})
        
        if result["mode"] == "safe":
            safe_count += 1
            assert result["action"] == "escalate"
            assert "Salto anómalo" in result["reason"]
        else:
            normal_count += 1
    
    assert safe_count == 100, f"Esperado 100 em modo seguro, obtido {safe_count}"
    assert normal_count == 0, f"Esperado 0 em modo normal, obtido {normal_count}"
    
    # Desativar e verificar que volta ao normal
    kill_switch.deactivate(deactivated_by="ops-admin", reason="Problema resolvido")
    assert kill_switch.active is False
    
    result_after = kill_switch.process_request({"action": "decide"})
    assert result_after["mode"] == "normal"

# ─── Teste 3: Shadow mode não afeta decisões reais ──────────────────────────
def test_shadow_mode_no_real_impact(shadow_deployer):
    """Teste 3: nova versão em shadow mode gera comparação sem afetar decisões reais."""
    
    # Duas versões de "modelo" (funções simuladas)
    def active_model(request):
        return {"decision": "approved", "score": 0.85, "version": "v1.0.0"}
    
    def shadow_model(request):
        # Shadow é diferente (nova versão candidata)
        return {"decision": "approved", "score": 0.92, "version": "v2.0.0"}
    
    # Configurar shadow
    shadow_deployer.set_shadow("v2.0.0")
    assert shadow_deployer.shadow_version == "v2.0.0"
    
    # Executar 20 pedidos em shadow mode
    real_outputs = []
    for i in range(20):
        result = shadow_deployer.run_shadow(
            trace_id=f"T-{i:03d}",
            request={"id": i},
            active_fn=active_model,
            shadow_fn=shadow_model
        )
        
        # A decisão real deve vir SEMPRE do active
        assert result["mode"] == "shadow"
        assert result["version"] == "v1.0.0"  # Decisão real usa active
        assert result["shadow_compared"] == "v2.0.0"
        assert result["output"]["version"] == "v1.0.0"  # Output é do active
        
        real_outputs.append(result["output"])
    
    # Verificar que TODAS as decisões reais vieram do active
    for output in real_outputs:
        assert output["version"] == "v1.0.0"
        assert output["score"] == 0.85  # Score do active, não do shadow
    
    # Estatísticas de comparação
    stats = shadow_deployer.get_comparison_stats()
    assert stats["total"] == 20
    assert stats["match_rate"] == 0.0  # Diferem no score
    assert stats["mismatches"] == 20
    
    # Verificar que não houve impacto real
    assert shadow_deployer.verify_no_real_impact() is True
