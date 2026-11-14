"""Gestão de golden datasets e testes de regressão."""
from typing import Dict, Any, List
from pydantic import BaseModel, Field
from datetime import datetime, timezone

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

class GoldenSetItem(BaseModel):
    id: str
    input_data: Dict[str, Any]
    expected_output: Dict[str, Any]
    category: str
    difficulty: str = "medium"

class GoldenSet(BaseModel):
    name: str
    version: str
    description: str
    items: List[GoldenSetItem]
    created_at: datetime = Field(default_factory=utc_now)

class RegressionTestResult(BaseModel):
    golden_set_name: str
    golden_set_version: str
    total_items: int
    passed: int
    failed: int
    accuracy: float
    regressions: List[Dict[str, Any]] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=utc_now)
    
    def is_acceptable(self, threshold: float = 0.95) -> bool:
        return self.accuracy >= threshold

class RegressionTester:
    def __init__(self):
        self.golden_sets: Dict[str, GoldenSet] = {}
    
    def register_golden_set(self, golden_set: GoldenSet):
        key = f"{golden_set.name}_{golden_set.version}"
        self.golden_sets[key] = golden_set
    
    def run_regression_test(self, golden_set_name: str, version: str,
                           model_fn, threshold: float = 0.95) -> RegressionTestResult:
        key = f"{golden_set_name}_{version}"
        if key not in self.golden_sets:
            raise ValueError(f"Golden set {key} não encontrado")
        
        golden_set = self.golden_sets[key]
        passed = 0
        failed = 0
        regressions = []
        
        for item in golden_set.items:
            try:
                predicted = model_fn(item.input_data)
                if self._compare_outputs(predicted, item.expected_output):
                    passed += 1
                else:
                    failed += 1
                    regressions.append({
                        "item_id": item.id,
                        "category": item.category,
                        "expected": item.expected_output,
                        "predicted": predicted
                    })
            except Exception as e:
                failed += 1
                regressions.append({"item_id": item.id, "error": str(e)})
        
        total = passed + failed
        accuracy = passed / total if total > 0 else 0.0
        
        return RegressionTestResult(
            golden_set_name=golden_set_name,
            golden_set_version=version,
            total_items=total,
            passed=passed,
            failed=failed,
            accuracy=accuracy,
            regressions=regressions
        )
    
    def _compare_outputs(self, predicted: Dict[str, Any], expected: Dict[str, Any]) -> bool:
        for key, expected_value in expected.items():
            if key not in predicted or predicted[key] != expected_value:
                return False
        return True
