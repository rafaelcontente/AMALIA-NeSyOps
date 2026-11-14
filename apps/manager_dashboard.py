"""Painel do gestor: métricas do monitor."""
from typing import Dict, Any, List
from datetime import datetime, timezone, timedelta
from pydantic import BaseModel

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

class DashboardMetrics(BaseModel):
    """Métricas do painel do gestor."""
    total_decisions: int
    automatic_decisions: int
    escalated_decisions: int
    human_reviewed: int
    avg_decision_time_seconds: float
    error_rate: float
    drift_alerts: int
    active_alerts: int

class ManagerDashboard:
    """Painel do gestor: métricas do monitor."""
    
    def __init__(self, api_client):
        self.api_client = api_client
    
    def get_metrics(self, period_hours: int = 24) -> DashboardMetrics:
        """Obtém métricas do período especificado."""
        metrics_data = self.api_client.get_dashboard_metrics(period_hours)
        
        return DashboardMetrics(
            total_decisions=metrics_data.get("total_decisions", 0),
            automatic_decisions=metrics_data.get("automatic_decisions", 0),
            escalated_decisions=metrics_data.get("escalated_decisions", 0),
            human_reviewed=metrics_data.get("human_reviewed", 0),
            avg_decision_time_seconds=metrics_data.get("avg_decision_time_seconds", 0.0),
            error_rate=metrics_data.get("error_rate", 0.0),
            drift_alerts=metrics_data.get("drift_alerts", 0),
            active_alerts=metrics_data.get("active_alerts", 0)
        )
    
    def get_alerts(self) -> List[Dict[str, Any]]:
        """Obtém alertas ativos."""
        return self.api_client.get_active_alerts()
    
    def get_drift_report(self) -> Dict[str, Any]:
        """Obtém relatório de drift."""
        return self.api_client.get_drift_report()
    
    def acknowledge_alert(self, alert_id: str, manager_id: str) -> Dict[str, Any]:
        """Reconhece um alerta."""
        return self.api_client.acknowledge_alert(alert_id, manager_id)
    
    def export_report(self, period_hours: int = 24, format: str = "pdf") -> str:
        """Exporta relatório de métricas."""
        metrics = self.get_metrics(period_hours)
        
        if format == "json":
            import json
            return json.dumps(metrics.model_dump(), indent=2)
        elif format == "pdf":
            return f"PDF report for last {period_hours} hours (mock)"
        else:
            raise ValueError(f"Formato não suportado: {format}")
