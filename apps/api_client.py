"""Cliente API mock para as aplicações."""
from typing import Dict, Any, List
from datetime import datetime, timezone

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

class MockAPIClient:
    """Cliente API mock para testes."""
    
    def __init__(self):
        self.cases = {}
        self.decisions = {}
        self.audit_log = []
    
    def get_case(self, trace_id: str) -> Dict[str, Any]:
        """Obtém dados de um caso."""
        return {
            "title": f"Caso {trace_id}",
            "original_text": "Texto original do documento...",
            "highlighted_excerpt": "Excerto relevante destacado...",
            "evidences": [
                {"id": "EV-001", "type": "document", "content": "Evidência 1"}
            ],
            "failed_rules": [
                {"id": "R-001", "name": "Regra falhada", "reason": "Motivo"}
            ],
            "rules_version": "v1.0.0",
            "proposed_decision": {"status": "pending"}
        }
    
    def submit_reviewer_decision(self, trace_id: str, decision: str,
                                justification: str, reviewer_id: str) -> Dict[str, Any]:
        """Submete decisão do revisor."""
        record = {
            "trace_id": trace_id,
            "decision": decision,
            "justification": justification,
            "reviewer_id": reviewer_id,
            "timestamp": utc_now()
        }
        
        self.decisions[trace_id] = record
        self.audit_log.append({
            "event": "reviewer_decision",
            "data": record
        })
        
        return {"status": "success", "trace_id": trace_id}
    
    def get_reviewer_queue(self, reviewer_id: str) -> List[Dict[str, Any]]:
        """Obtém fila de casos para revisor."""
        return [
            {"trace_id": "T-001", "title": "Caso 1", "priority": "high"},
            {"trace_id": "T-002", "title": "Caso 2", "priority": "medium"}
        ]
    
    def get_audit_timeline(self, trace_id: str) -> List[Dict[str, Any]]:
        """Obtém linha do tempo de auditoria."""
        return [
            {
                "timestamp": utc_now().isoformat(),
                "event_type": "case_created",
                "actor": "system",
                "details": {"trace_id": trace_id}
            },
            {
                "timestamp": utc_now().isoformat(),
                "event_type": "decision_made",
                "actor": "gate",
                "details": {"status": "escalated"}
            }
        ]
    
    def verify_audit_integrity(self, trace_id: str) -> Dict[str, Any]:
        """Verifica integridade da cadeia de auditoria."""
        return {
            "valid": True,
            "broken_at": None,
            "message": "Cadeia íntegra"
        }
    
    def search_audit_events(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Pesquisa eventos de auditoria."""
        return self.audit_log
    
    def get_dashboard_metrics(self, period_hours: int) -> Dict[str, Any]:
        """Obtém métricas do painel."""
        return {
            "total_decisions": 100,
            "automatic_decisions": 85,
            "escalated_decisions": 15,
            "human_reviewed": 15,
            "avg_decision_time_seconds": 2.5,
            "error_rate": 0.02,
            "drift_alerts": 0,
            "active_alerts": 0
        }
    
    def get_active_alerts(self) -> List[Dict[str, Any]]:
        """Obtém alertas ativos."""
        return []
    
    def get_drift_report(self) -> Dict[str, Any]:
        """Obtém relatório de drift."""
        return {"drift_detected": False, "features": []}
    
    def acknowledge_alert(self, alert_id: str, manager_id: str) -> Dict[str, Any]:
        """Reconhece alerta."""
        return {"status": "acknowledged", "alert_id": alert_id}
    
    def validate_rule_expression(self, expression: str) -> Dict[str, Any]:
        """Valida expressão de regra."""
        # Simulação simples
        valid = "==" in expression or ">" in expression or "<" in expression
        return {
            "valid": valid,
            "errors": [] if valid else ["Expressão inválida"],
            "warnings": []
        }
    
    def run_rule_tests(self, expression: str, test_cases: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Executa testes de regra."""
        results = []
        for test in test_cases:
            # Simulação simples
            results.append({
                "input": test["input_data"],
                "expected": test["expected_result"],
                "actual": True,  # Simulação
                "passed": True
            })
        
        return {
            "total": len(results),
            "passed": len(results),
            "failed": 0,
            "results": results
        }
    
    def submit_rule_for_review(self, draft: Dict[str, Any], jurist_id: str) -> Dict[str, Any]:
        """Submete regra para revisão."""
        self.audit_log.append({
            "event": "rule_submitted",
            "data": {"draft": draft, "jurist_id": jurist_id}
        })
        
        return {"status": "submitted", "rule_id": "R-NEW-001"}
