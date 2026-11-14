"""Avaliador de Golden Set com métricas desagregadas por categoria."""
import json
from typing import Dict, Any, List
from collections import defaultdict
from datetime import datetime

class CategoryEvaluator:
    """Avalia decisões contra um golden set, calculando métricas globais e por categoria."""
    
    def __init__(self, golden_set_path: str = "eval/golden_set_v3.json"):
        with open(golden_set_path, "r", encoding="utf-8") as f:
            self.cases = json.load(f)
    
    def evaluate(self, decision_func) -> Dict[str, Any]:
        """
        Avalia todas as casos usando a função de decisão fornecida.
        decision_func(case) deve retornar {"decision": "approved"|"rejected", "rules_violated": [...]}
        """
        global_metrics = {"tp": 0, "tn": 0, "fp": 0, "fn": 0}
        category_metrics = defaultdict(lambda: {"tp": 0, "tn": 0, "fp": 0, "fn": 0, "total": 0})
        errors = []
        
        for case in self.cases:
            try:
                result = decision_func(case)
                pred_decision = result.get("decision", "unknown")
                pred_violated = set(result.get("rules_violated", []))
                
                exp_decision = case["expected_decision"]
                exp_violated = set(case["expected_rules_violated"])
                category = case["category"]
                
                # Atualizar métricas globais
                self._update_metrics(global_metrics, pred_decision, exp_decision)
                
                # Atualizar métricas por categoria
                self._update_metrics(category_metrics[category], pred_decision, exp_decision)
                category_metrics[category]["total"] += 1
                
                # Detetar erros de regras (opcional, para debugging)
                if pred_violated != exp_violated:
                    errors.append({
                        "case_id": case["id"],
                        "expected_violated": list(exp_violated),
                        "predicted_violated": list(pred_violated)
                    })
                    
            except Exception as e:
                errors.append({"case_id": case["id"], "error": str(e)})
        
        return self._compile_report(global_metrics, category_metrics, errors)
    
    def _update_metrics(self, metrics: Dict[str, int], pred: str, exp: str):
        if pred == "approved" and exp == "approved":
            metrics["tp"] += 1
        elif pred == "rejected" and exp == "rejected":
            metrics["tn"] += 1
        elif pred == "rejected" and exp == "approved":
            metrics["fp"] += 1
        elif pred == "approved" and exp == "rejected":
            metrics["fn"] += 1
    
    def _calc_stats(self, tp: int, tn: int, fp: int, fn: int) -> Dict[str, float]:
        total = tp + tn + fp + fn
        accuracy = (tp + tn) / total if total > 0 else 0.0
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
        
        return {
            "accuracy": round(accuracy, 4),
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1_score": round(f1, 4),
            "total_cases": total
        }
    
    def _compile_report(self, global_metrics: Dict, category_metrics: Dict, errors: List) -> Dict[str, Any]:
        report = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "golden_set_version": "v3",
            "global_metrics": self._calc_stats(**global_metrics),
            "category_metrics": {},
            "errors": errors[:10], # Limitar a 10 erros no report para não ficar gigante
            "total_errors": len(errors)
        }
        
        for cat, metrics in category_metrics.items():
            report["category_metrics"][cat] = self._calc_stats(
                metrics["tp"], metrics["tn"], metrics["fp"], metrics["fn"]
            )
            
        return report
