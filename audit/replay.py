"""
Motor de replay: reproduz a parte determinística de uma decisão.
Compara o resultado com o original para detetar alterações.
"""
from typing import Dict, Any, Optional
from audit.entry import AuditEntry
from policy.engine import RuleEvaluator
from policy.models import RuleSet

class ReplayEngine:
    """Reproduz decisões a partir do ledger de auditoria."""
    
    def __init__(self, rule_registry):
        self.rule_registry = rule_registry
    
    def replay(self, entry: AuditEntry, rule_set: Optional[RuleSet] = None) -> Dict[str, Any]:
        """
        Reproduz a parte determinística de uma decisão.
        Retorna: {"match": bool, "original": dict, "replayed": dict, "diff": list}
        """
        # Obter conjunto de regras (usar versão do entry)
        if rule_set is None:
            if entry.rules_version in self.rule_registry.rule_sets:
                rule_set = self.rule_registry.get_rule_set(entry.rules_version)
            else:
                return {
                    "match": False,
                    "error": f"Conjunto de regras {entry.rules_version} não encontrado"
                }
        
        # Reproduzir avaliação de regras
        evaluator = RuleEvaluator(rule_set)
        
        # Preparar contexto de avaliação
        eval_context = entry.input_data.copy()
        
        # Avaliar regras
        results = evaluator.evaluate(eval_context)
        
        # Construir veredito reproduzido
        replayed_verdict = {
            "rules_evaluated": [r["rule_id"] for r in results],
            "rules_violated": [r["rule_id"] for r in results if not r["passed"] and r["severity"] == "hard"],
            "passed": all(r["passed"] or r["severity"] == "soft" for r in results)
        }
        
        # Comparar com o original
        original_verdict = {
            "rules_evaluated": entry.rules_evaluated,
            "rules_violated": entry.rules_violated,
            "passed": len(entry.rules_violated) == 0
        }
        
        # Calcular diferenças
        diff = []
        if set(replayed_verdict["rules_evaluated"]) != set(original_verdict["rules_evaluated"]):
            diff.append("rules_evaluated")
        if set(replayed_verdict["rules_violated"]) != set(original_verdict["rules_violated"]):
            diff.append("rules_violated")
        if replayed_verdict["passed"] != original_verdict["passed"]:
            diff.append("passed")
        
        return {
            "match": len(diff) == 0,
            "original": original_verdict,
            "replayed": replayed_verdict,
            "diff": diff
        }
