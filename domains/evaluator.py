"""Avaliador de concordância entre decisões automáticas e especialistas."""
from typing import Dict, Any, List
from datetime import datetime, timezone

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

class DomainEvaluator:
    """Avalia concordância entre decisões automáticas e especialistas."""
    
    def __init__(self):
        self.evaluations: List[Dict[str, Any]] = []
    
    def evaluate_agreement(self, 
                          automatic_decisions: Dict[str, Dict[str, Any]],
                          expert_decisions: Dict[str, Dict[str, Any]],
                          threshold: float = 0.85) -> Dict[str, Any]:
        """
        Avalia concordância entre decisões automáticas e especialistas.
        
        Args:
            automatic_decisions: Decisões automáticas {case_id: {decision, ...}}
            expert_decisions: Decisões de especialistas {case_id: {decision, ...}}
            threshold: Limiar mínimo de concordância
        
        Returns:
            Resultado da avaliação
        """
        total_cases = 0
        agreements = 0
        disagreements = []
        
        for case_id, auto_decision in automatic_decisions.items():
            if case_id not in expert_decisions:
                continue
            
            expert_decision = expert_decisions[case_id]
            total_cases += 1
            
            # Comparar decisões
            if auto_decision.get("decision") == expert_decision.get("decision"):
                agreements += 1
            else:
                disagreements.append({
                    "case_id": case_id,
                    "automatic": auto_decision.get("decision"),
                    "expert": expert_decision.get("decision"),
                    "auto_confidence": auto_decision.get("confidence", 0),
                    "expert_confidence": expert_decision.get("confidence", 0)
                })
        
        agreement_rate = agreements / total_cases if total_cases > 0 else 0
        
        result = {
            "total_cases": total_cases,
            "agreements": agreements,
            "disagreements": len(disagreements),
            "agreement_rate": agreement_rate,
            "threshold": threshold,
            "meets_threshold": agreement_rate >= threshold,
            "disagreement_details": disagreements,
            "timestamp": utc_now()
        }
        
        self.evaluations.append(result)
        return result
    
    def evaluate_pack(self, pack, decision_fn) -> Dict[str, Any]:
        """
        Avalia um pack completo executando todos os casos do golden set.
        
        Args:
            pack: DomainPack a avaliar
            decision_fn: Função que toma decisão automática
        
        Returns:
            Resultado completo da avaliação
        """
        automatic_decisions = {}
        escalated_cases = []
        hard_rule_violations = []
        
        # Processar cada caso do golden set
        for case in pack.golden_set.cases:
            case_id = case["id"]
            
            # Verificar se está dentro do âmbito
            if not pack.is_in_scope(case):
                escalated_cases.append({
                    "case_id": case_id,
                    "reason": "Fora do âmbito do domínio"
                })
                continue
            
            # Tomar decisão automática
            try:
                decision = decision_fn(case)
                automatic_decisions[case_id] = decision
                
                # Verificar violações de regras duras
                if decision.get("status") == "rejected":
                    for rule_id in decision.get("violated_rules", []):
                        if rule_id in pack.policy.hard_rules:
                            hard_rule_violations.append({
                                "case_id": case_id,
                                "rule_id": rule_id
                            })
            except Exception as e:
                escalated_cases.append({
                    "case_id": case_id,
                    "reason": f"Erro no processamento: {str(e)}"
                })
        
        # Avaliar concordância
        agreement_result = self.evaluate_agreement(
            automatic_decisions,
            pack.golden_set.expert_decisions,
            pack.golden_set.agreement_threshold
        )
        
        # Resultado completo
        result = {
            "pack_id": pack.pack_id,
            "version": pack.version,
            "total_cases": len(pack.golden_set.cases),
            "automatic_decisions": len(automatic_decisions),
            "escalated_cases": len(escalated_cases),
            "hard_rule_violations": len(hard_rule_violations),
            "agreement": agreement_result,
            "escalation_details": escalated_cases,
            "violation_details": hard_rule_violations,
            "timestamp": utc_now()
        }
        
        return result
