"""Consola do revisor: fila de casos, evidência lado a lado com texto, regras falhadas."""
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

class ReviewerCaseView(BaseModel):
    """Vista de um caso para o revisor."""
    trace_id: str
    case_title: str
    original_text: str
    highlighted_excerpt: str
    evidences: List[Dict[str, Any]]
    failed_rules: List[Dict[str, Any]]
    rules_version: str
    proposed_decision: Optional[Dict[str, Any]] = None
    reviewer_actions: List[str] = ["approve", "correct", "reject", "request_info"]

class ReviewerConsole:
    """Consola do revisor: só consome API, nunca decide."""
    
    def __init__(self, api_client):
        self.api_client = api_client
        self.action_log: List[Dict[str, Any]] = []
    
    def load_case(self, trace_id: str) -> ReviewerCaseView:
        """
        Carrega caso para revisão.
        Só consome API, nunca decide.
        """
        # Chamar API para obter dados do caso
        case_data = self.api_client.get_case(trace_id)
        
        # Construir vista do revisor
        view = ReviewerCaseView(
            trace_id=trace_id,
            case_title=case_data.get("title", f"Caso {trace_id}"),
            original_text=case_data.get("original_text", ""),
            highlighted_excerpt=case_data.get("highlighted_excerpt", ""),
            evidences=case_data.get("evidences", []),
            failed_rules=case_data.get("failed_rules", []),
            rules_version=case_data.get("rules_version", "unknown"),
            proposed_decision=case_data.get("proposed_decision")
        )
        
        return view
    
    def submit_decision(self, trace_id: str, decision: str, 
                       justification: str, reviewer_id: str) -> Dict[str, Any]:
        """
        Submete decisão do revisor via API.
        Gera registo no audit.
        """
        # Validar que decisão é válida
        valid_decisions = ["approve", "correct", "reject", "request_info"]
        if decision not in valid_decisions:
            raise ValueError(f"Decisão inválida: {decision}")
        
        # Chamar API para submeter decisão
        result = self.api_client.submit_reviewer_decision(
            trace_id=trace_id,
            decision=decision,
            justification=justification,
            reviewer_id=reviewer_id
        )
        
        # Registar ação
        action_record = {
            "trace_id": trace_id,
            "decision": decision,
            "justification": justification,
            "reviewer_id": reviewer_id,
            "timestamp": utc_now(),
            "api_response": result
        }
        self.action_log.append(action_record)
        
        return result
    
    def get_queue(self, reviewer_id: str) -> List[Dict[str, Any]]:
        """Obtém fila de casos para o revisor."""
        return self.api_client.get_reviewer_queue(reviewer_id)
    
    def get_action_log(self) -> List[Dict[str, Any]]:
        """Retorna log de ações do revisor."""
        return self.action_log
