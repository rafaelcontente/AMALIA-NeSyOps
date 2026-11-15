"""
Modo Piloto (Pilot Mode).
Intercepta todas as decisões para revisão humana obrigatória e registo de incidentes.
"""
import os
from typing import Dict, Any, Optional
from review.queue import ReviewQueue, EscalatedCase
from review.incidents import IncidentManager


class PilotModeManager:
    """
    Gestor do Modo Piloto.
    Quando ativo, força todas as decisões para a fila de revisão e cria incidentes.
    """

    def __init__(self, review_queue: ReviewQueue, incident_manager: IncidentManager):
        self.review_queue = review_queue
        self.incident_manager = incident_manager
        self.is_active = os.getenv("PILOT_MODE", "false").lower() == "true"

    def intercept_decision(
        self,
        trace_id: str,
        decision_result: Dict[str, Any],
        proposal: Optional[Dict[str, Any]] = None,
        proposer_id: str = "pilot-agent",
    ) -> Dict[str, Any]:
        """
        Intercepta uma decisão. Se o modo piloto estiver ativo:
        1. Envia para a fila de revisão (mesmo que seja APPROVED).
        2. Cria um incidente de "Pilot Monitoring".
        """
        if not self.is_active:
            return decision_result

        # 1. Escalar para revisão (satisfaz campos obrigatórios de EscalatedCase)
        case = EscalatedCase(
            trace_id=trace_id,
            proposal=proposal or decision_result.get("proposal", {}),
            proposer_id=proposer_id,
            confidence=0.0,  # Força revisão humana
            risk_score=0.5,
        )
        self.review_queue.add(case)

        # 2. Registar incidente de monitorização
        self.incident_manager.report_incident(
            severity="low",
            title=f"Pilot Decision Monitor: {trace_id}",
            description=f"Decision processed in pilot mode: {decision_result}",
            affected_component="gate/pilot_mode.py",
        )

        # Modificar o resultado para indicar revisão pendente
        decision_result["pilot_status"] = "pending_review"
        if "verdict" in decision_result and isinstance(decision_result["verdict"], dict):
            decision_result["verdict"]["status"] = "pending_review"

        return decision_result
