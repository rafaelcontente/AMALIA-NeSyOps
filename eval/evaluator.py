"""Evaluator com métricas granulares por categoria."""
import json
from typing import Dict, Any, List
from dataclasses import dataclass
from datetime import datetime, timezone
from collections import defaultdict

@dataclass
class CategoryMetrics:
    """Métricas para uma categoria específica."""
    category: str
    total: int
    correct: int
    false_positives: int
    false_negatives: int
    escalations: int
    
    @property
    def accuracy(self) -> float:
        return self.correct / self.total if self.total > 0 else 0.0
    
    @property
    def fp_rate(self) -> float:
        return self.false_positives / self.total if self.total > 0 else 0.0
    
    @property
    def fn_rate(self) -> float:
        return self.false_negatives / self.total if self.total > 0 else 0.0
    
    @property
    def escalation_rate(self) -> float:
        return self.escalations / self.total if self.total > 0 else 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "category": self.category,
            "total": self.total,
            "correct": self.correct,
            "false_positives": self.false_positives,
            "false_negatives": self.false_negatives,
            "escalations": self.escalations,
            "accuracy": round(self.accuracy, 3),
            "fp_rate": round(self.fp_rate, 3),
            "fn_rate": round(self.fn_rate, 3),
            "escalation_rate": round(self.escalation_rate, 3),
        }

class GoldenSetEvaluator:
    """Avalia o sistema contra um golden set com métricas por categoria."""
    
    def __init__(self):
        self.results: List[Dict[str, Any]] = []
    
    def evaluate_case(self, case: Dict[str, Any], decision_fn) -> Dict[str, Any]:
        """
        Avalia um caso individual.
        
        Args:
            case: Dicionário com id, category, input_data, expected_decision
            decision_fn: Função que recebe input_data e retorna {"status": "approved|rejected|escalated"}
        
        Returns:
            Dicionário com resultado detalhado
        """
        result = decision_fn(case["input_data"])
        actual = result.get("status", "unknown")
        expected = case["expected_decision"]
        
        is_correct = actual == expected
        is_fp = actual == "approved" and expected != "approved"
        is_fn = actual != "approved" and expected == "approved"
        is_escalation = actual == "escalated"
        
        return {
            "case_id": case["id"],
            "category": case["category"],
            "expected": expected,
            "actual": actual,
            "correct": is_correct,
            "false_positive": is_fp,
            "false_negative": is_fn,
            "escalation": is_escalation,
            "explanation": result.get("explanation", ""),
            "rules_violated": result.get("rules_violated", []),
        }
    
    def evaluate_golden_set(self, cases: List[Dict[str, Any]], decision_fn) -> Dict[str, Any]:
        """
        Avalia todo o golden set e retorna métricas agregadas.
        
        Args:
            cases: Lista de casos do golden set
            decision_fn: Função de decisão
        
        Returns:
            Relatório completo com métricas globais e por categoria
        """
        # Avaliar cada caso
        self.results = [self.evaluate_case(case, decision_fn) for case in cases]
        
        # Métricas globais
        total = len(self.results)
        correct = sum(1 for r in self.results if r["correct"])
        fps = sum(1 for r in self.results if r["false_positive"])
        fns = sum(1 for r in self.results if r["false_negative"])
        escalations = sum(1 for r in self.results if r["escalation"])
        
        # Métricas por categoria
        by_category = defaultdict(lambda: {"total": 0, "correct": 0, "fp": 0, "fn": 0, "esc": 0})
        for r in self.results:
            cat = r["category"]
            by_category[cat]["total"] += 1
            if r["correct"]:
                by_category[cat]["correct"] += 1
            if r["false_positive"]:
                by_category[cat]["fp"] += 1
            if r["false_negative"]:
                by_category[cat]["fn"] += 1
            if r["escalation"]:
                by_category[cat]["esc"] += 1
        
        category_metrics = []
        for cat, data in sorted(by_category.items()):
            metrics = CategoryMetrics(
                category=cat,
                total=data["total"],
                correct=data["correct"],
                false_positives=data["fp"],
                false_negatives=data["fn"],
                escalations=data["esc"],
            )
            category_metrics.append(metrics)
        
        report = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "total_cases": total,
            "global_metrics": {
                "accuracy": round(correct / total, 3) if total > 0 else 0.0,
                "false_positive_rate": round(fps / total, 3) if total > 0 else 0.0,
                "false_negative_rate": round(fns / total, 3) if total > 0 else 0.0,
                "escalation_rate": round(escalations / total, 3) if total > 0 else 0.0,
            },
            "category_metrics": [m.to_dict() for m in category_metrics],
            "failures": [
                {
                    "case_id": r["case_id"],
                    "category": r["category"],
                    "expected": r["expected"],
                    "actual": r["actual"],
                    "rules_violated": r["rules_violated"],
                }
                for r in self.results
                if not r["correct"]
            ],
        }
        
        return report
    
    def save_report(self, report: Dict[str, Any], path: str):
        """Guarda o relatório em JSON."""
        with open(path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"Report saved to {path}")
