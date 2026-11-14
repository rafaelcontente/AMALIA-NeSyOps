"""
Amostragem de auditoria pós-hoc sobre casos decididos automaticamente.
"""
from typing import List, Dict, Any
from review.queue import ReviewQueue, EscalatedCase
from review.interface import HumanDecision
import random

class PostHocAuditor:
    """Auditor pós-hoc para casos decididos automaticamente."""
    
    def __init__(self, queue: ReviewQueue, sample_rate: float = 0.1):
        self.queue = queue
        self.sample_rate = sample_rate  # 10% por defeito
        self.audited_cases: List[str] = []
    
    def select_cases_for_audit(self, auto_decided_cases: List[EscalatedCase]) -> List[EscalatedCase]:
        """
        Seleciona casos decididos automaticamente para auditoria.
        Usa amostragem estratificada por risco.
        """
        if not auto_decided_cases:
            return []
        
        # Estratificar por risco
        high_risk = [c for c in auto_decided_cases if c.risk_score > 0.7]
        medium_risk = [c for c in auto_decided_cases if 0.3 <= c.risk_score <= 0.7]
        low_risk = [c for c in auto_decided_cases if c.risk_score < 0.3]
        
        # Amostragem: mais casos de alto risco
        selected = []
        
        # Alto risco: 30% de amostragem
        high_sample_size = max(1, int(len(high_risk) * 0.3))
        selected.extend(random.sample(high_risk, min(high_sample_size, len(high_risk))))
        
        # Médio risco: 10% de amostragem
        medium_sample_size = max(1, int(len(medium_risk) * 0.1))
        selected.extend(random.sample(medium_risk, min(medium_sample_size, len(medium_risk))))
        
        # Baixo risco: 5% de amostragem
        low_sample_size = max(1, int(len(low_risk) * 0.05))
        selected.extend(random.sample(low_risk, min(low_sample_size, len(low_risk))))
        
        # Registar casos auditados
        self.audited_cases.extend([c.id for c in selected])
        
        return selected
    
    def get_audit_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas de auditoria."""
        return {
            "total_audited": len(self.audited_cases),
            "sample_rate": self.sample_rate,
            "audited_case_ids": self.audited_cases
        }
