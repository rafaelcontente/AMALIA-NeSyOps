"""
Plano de ação quando a validação falha: reparar, degradar, escalar ou recusar.
"""
from typing import Dict, Any, Optional
from gate.validator import ValidationResult

class FailPlan:
    REPAIR = "repair"
    DEGRADE = "degrade"
    ESCALATE = "escalate"
    REFUSE = "refuse"

class FailurePlanner:
    """Decide o plano de ação com base nas falhas detetadas."""
    
    def __init__(self, max_repair_attempts: int = 2):
        self.max_repair_attempts = max_repair_attempts
    
    def decide_plan(self, validation_results: list[ValidationResult], 
                    repair_attempt: int = 0) -> Dict[str, Any]:
        """
        Decide o plano de ação:
        - REPAIR: se é recuperável e ainda dentro do limite de tentativas
        - DEGRADE: se podemos devolver resultado parcial
        - ESCALATE: se precisa de humano (ex: ambiguidade)
        - REFUSE: se falha crítica ou limite de reparação excedido
        """
        failed_layers = [r for r in validation_results if not r.passed]
        
        if not failed_layers:
            return {"action": FailPlan.REPAIR, "reason": "Sem falhas", "needs_approval": False}
        
        # Se já excedeu o limite de tentativas de reparação
        if repair_attempt >= self.max_repair_attempts:
            return {
                "action": FailPlan.ESCALATE,
                "reason": f"Limite de {self.max_repair_attempts} tentativas de reparação excedido",
                "failed_layers": [r.layer for r in failed_layers],
                "needs_approval": True
            }
        
        # Camadas que permitem reparação
        repairable_layers = {"consistency", "claims"}
        last_failed = failed_layers[-1]
        
        # Falhas críticas (estrutura, regras duras) = recusar ou escalar
        if last_failed.layer == "structure":
            return {
                "action": FailPlan.REFUSE,
                "reason": f"Falha estrutural não reparável: {last_failed.reason}",
                "needs_approval": False
            }
        
        if last_failed.layer == "domain_rules":
            return {
                "action": FailPlan.REFUSE,
                "reason": f"Violação de regra de domínio: {last_failed.reason}",
                "needs_approval": False
            }
        
        # Falhas recuperáveis
        if last_failed.layer in repairable_layers:
            return {
                "action": FailPlan.REPAIR,
                "reason": f"Falha em {last_failed.layer} é reparável: {last_failed.reason}",
                "attempt": repair_attempt + 1,
                "needs_approval": False
            }
        
        # Plausibilidade = escalar (pode ser ambiguidade)
        if last_failed.layer == "plausibility":
            return {
                "action": FailPlan.ESCALATE,
                "reason": f"Plausibilidade baixa requer revisão humana: {last_failed.reason}",
                "needs_approval": True
            }
        
        # Default: escalar por segurança
        return {
            "action": FailPlan.ESCALATE,
            "reason": "Falha não classificada, escalado por segurança",
            "needs_approval": True
        }
