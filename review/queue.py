"""
Fila de casos escalados com prioridade por risco, confiança e prazo.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from uuid import uuid4
from pydantic import BaseModel, Field, ConfigDict
import heapq

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

class EscalatedCase(BaseModel):
    """Caso escalado para revisão humana."""
    model_config = ConfigDict(frozen=True)
    
    id: str = Field(default_factory=lambda: str(uuid4()))
    trace_id: str
    proposal: Dict[str, Any]
    evidences: List[Dict[str, Any]] = Field(default_factory=list)
    failed_rules: List[str] = Field(default_factory=list)
    alternatives: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Prioridade
    risk_score: float = 0.0  # 0-1, maior = mais risco
    confidence: float = 0.5  # 0-1, menor = menos confiança
    deadline: Optional[datetime] = None
    
    # Metadados
    proposer_id: str  # Quem gerou a proposta (para maker-checker)
    created_at: datetime = Field(default_factory=utc_now)
    status: str = "pending"  # pending, approved, rejected, corrected
    
    def priority_score(self) -> float:
        """Calcula score de prioridade (menor = mais prioritário)."""
        # Risco alto = prioridade alta (score baixo)
        # Confiança baixa = prioridade alta
        # Prazo curto = prioridade alta
        
        risk_factor = 1.0 - self.risk_score
        confidence_factor = self.confidence
        
        # Prazo (se existir)
        if self.deadline:
            now = utc_now()
            hours_left = (self.deadline - now).total_seconds() / 3600
            deadline_factor = max(0, min(1, hours_left / 24))  # Normalizar para 0-1 (24h)
        else:
            deadline_factor = 0.5
        
        # Score combinado (menor = mais prioritário)
        return risk_factor * 0.5 + confidence_factor * 0.3 + deadline_factor * 0.2

class ReviewQueue:
    """Fila de revisão com prioridade."""
    
    def __init__(self):
        self._heap: List[tuple] = []  # (priority, case_id, case)
        self._cases: Dict[str, EscalatedCase] = {}
        self._counter = 0  # Para desempate em heapq
    
    def add(self, case: EscalatedCase) -> str:
        """Adiciona caso à fila com prioridade."""
        priority = case.priority_score()
        self._counter += 1
        
        # heapq é min-heap, então menor priority = maior prioridade
        heapq.heappush(self._heap, (priority, self._counter, case.id))
        self._cases[case.id] = case
        
        return case.id
    
    def get_next(self) -> Optional[EscalatedCase]:
        """Retorna o próximo caso de maior prioridade."""
        if not self._heap:
            return None
        
        _, _, case_id = heapq.heappop(self._heap)
        return self._cases.get(case_id)
    
    def get_case(self, case_id: str) -> Optional[EscalatedCase]:
        """Retorna caso por ID."""
        return self._cases.get(case_id)
    
    def update_case(self, case_id: str, updates: Dict[str, Any]) -> Optional[EscalatedCase]:
        """Atualiza caso (ex: status)."""
        if case_id not in self._cases:
            return None
        
        old_case = self._cases[case_id]
        updated_dict = old_case.model_dump()
        updated_dict.update(updates)
        
        new_case = EscalatedCase(**updated_dict)
        self._cases[case_id] = new_case
        
        return new_case
    
    def size(self) -> int:
        """Retorna tamanho da fila."""
        return len(self._heap)
    
    def get_all_cases(self) -> List[EscalatedCase]:
        """Retorna todos os casos (para auditoria)."""
        return list(self._cases.values())
