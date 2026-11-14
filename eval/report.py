"""Geração de relatórios de avaliação."""
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime, timezone
from .golden_set import RegressionTestResult
from .red_team import AttackResult
from .baseline import BaselineResult

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

class EvaluationReport(BaseModel):
    report_id: str
    timestamp: datetime = Field(default_factory=utc_now)
    regression_results: List[RegressionTestResult] = Field(default_factory=list)
    red_team_results: List[AttackResult] = Field(default_factory=list)
    baseline_result: Optional[BaselineResult] = None
    model_result: Optional[BaselineResult] = None
    baseline_comparison: Optional[Dict[str, Any]] = None
    overall_status: str = "unknown"
    critical_issues: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    
    def add_regression_result(self, result: RegressionTestResult):
        self.regression_results.append(result)
    
    def add_red_team_results(self, results: List[AttackResult]):
        self.red_team_results.extend(results)
    
    def set_baseline_comparison(self, baseline_result: BaselineResult,
                               model_result: BaselineResult,
                               comparison: Dict[str, Any]):
        self.baseline_result = baseline_result
        self.model_result = model_result
        self.baseline_comparison = comparison

class EvaluationReportGenerator:
    def __init__(self):
        self.report_counter = 0
    
    def generate_report(self, report_id: Optional[str] = None) -> EvaluationReport:
        if report_id is None:
            self.report_counter += 1
            report_id = f"EVAL-{self.report_counter:04d}"
        return EvaluationReport(report_id=report_id)
    
    def evaluate_and_report(self, 
                           regression_results: List[RegressionTestResult],
                           red_team_results: List[AttackResult],
                           baseline_result: Optional[BaselineResult] = None,
                           model_result: Optional[BaselineResult] = None,
                           baseline_comparison: Optional[Dict[str, Any]] = None,
                           regression_threshold: float = 0.95,
                           red_team_max_success: int = 0) -> EvaluationReport:
        report = self.generate_report()
        
        for result in regression_results:
            report.add_regression_result(result)
        
        report.add_red_team_results(red_team_results)
        
        if baseline_result and model_result and baseline_comparison:
            report.set_baseline_comparison(baseline_result, model_result, baseline_comparison)
        
        critical_issues = []
        recommendations = []
        overall_status = "pass"
        
        for result in regression_results:
            if not result.is_acceptable(regression_threshold):
                overall_status = "fail"
                critical_issues.append(
                    f"Regressão em {result.golden_set_name}: "
                    f"accuracy {result.accuracy:.2%} < {regression_threshold:.2%}"
                )
        
        successful_attacks = sum(1 for r in red_team_results if r.success)
        if successful_attacks > red_team_max_success:
            overall_status = "fail"
            critical_issues.append(
                f"{successful_attacks} ataques de red teaming bem-sucedidos"
            )
        
        if baseline_comparison:
            if baseline_comparison["justification_needed"]:
                if overall_status == "pass":
                    overall_status = "warning"
                critical_issues.append("Melhoria do modelo sobre baseline é inferior a 5%")
            
            if not baseline_comparison["model_wins"]:
                overall_status = "fail"
                critical_issues.append("Modelo não supera baseline simples")
        
        report.overall_status = overall_status
        report.critical_issues = critical_issues
        report.recommendations = recommendations
        
        return report
