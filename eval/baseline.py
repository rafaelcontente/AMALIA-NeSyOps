"""Baseline sem LLM para comparação."""
from typing import Dict, Any, List
from pydantic import BaseModel, Field
from datetime import datetime, timezone

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

class BaselineResult(BaseModel):
    baseline_name: str
    total_items: int
    correct: int
    accuracy: float
    category_breakdown: Dict[str, float] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=utc_now)

class BaselineEvaluator:
    def __init__(self):
        self.baselines: Dict[str, callable] = {}
    
    def register_baseline(self, name: str, baseline_fn: callable):
        self.baselines[name] = baseline_fn
    
    def evaluate_baseline(self, baseline_name: str, 
                         test_data: List[Dict[str, Any]]) -> BaselineResult:
        if baseline_name not in self.baselines:
            raise ValueError(f"Baseline '{baseline_name}' não registado")
        
        baseline_fn = self.baselines[baseline_name]
        correct = 0
        category_stats = {}
        
        for item in test_data:
            input_data = item["input"]
            expected_output = item["expected_output"]
            category = item.get("category", "general")
            
            if category not in category_stats:
                category_stats[category] = {"correct": 0, "total": 0}
            
            try:
                predicted_output = baseline_fn(input_data)
                if self._compare_outputs(predicted_output, expected_output):
                    correct += 1
                    category_stats[category]["correct"] += 1
                category_stats[category]["total"] += 1
            except Exception:
                category_stats[category]["total"] += 1
        
        total = len(test_data)
        accuracy = correct / total if total > 0 else 0.0
        
        category_breakdown = {}
        for category, stats in category_stats.items():
            if stats["total"] > 0:
                category_breakdown[category] = stats["correct"] / stats["total"]
        
        return BaselineResult(
            baseline_name=baseline_name,
            total_items=total,
            correct=correct,
            accuracy=accuracy,
            category_breakdown=category_breakdown
        )
    
    def compare_with_model(self, baseline_name: str, model_name: str,
                          baseline_result: BaselineResult,
                          model_result: BaselineResult) -> Dict[str, Any]:
        improvement = model_result.accuracy - baseline_result.accuracy
        
        return {
            "baseline_name": baseline_name,
            "model_name": model_name,
            "baseline_accuracy": baseline_result.accuracy,
            "model_accuracy": model_result.accuracy,
            "improvement": improvement,
            "improvement_percentage": (improvement / baseline_result.accuracy * 100) 
                                     if baseline_result.accuracy > 0 else 0,
            "model_wins": model_result.accuracy > baseline_result.accuracy,
            "justification_needed": improvement < 0.05
        }
    
    def _compare_outputs(self, predicted: Dict[str, Any], expected: Dict[str, Any]) -> bool:
        for key, expected_value in expected.items():
            if key not in predicted or predicted[key] != expected_value:
                return False
        return True
