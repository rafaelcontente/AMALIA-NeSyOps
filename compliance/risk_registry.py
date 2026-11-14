"""
Registo de riscos: identificação, avaliação e mitigação.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field, ConfigDict
from enum import Enum

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

class RiskSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class RiskLikelihood(str, Enum):
    RARE = "rare"
    UNLIKELY = "unlikely"
    POSSIBLE = "possible"
    LIKELY = "likely"
    ALMOST_CERTAIN = "almost_certain"

class RiskEntry(BaseModel):
    """Entrada no registo de riscos."""
    model_config = ConfigDict(frozen=True)
    
    risk_id: str
    title: str
    description: str
    category: str  # "technical", "legal", "ethical", "operational"
    
    severity: RiskSeverity
    likelihood: RiskLikelihood
    
    affected_components: List[str] = Field(default_factory=list)
    affected_rules: List[str] = Field(default_factory=list)
    
    mitigations: List[str] = Field(default_factory=list)
    residual_risk: RiskSeverity = RiskSeverity.LOW
    
    owner: str  # Responsável pela gestão do risco
    status: str = "open"  # "open", "mitigated", "accepted", "closed"
    
    created_at: datetime = Field(default_factory=utc_now)
    last_reviewed: datetime = Field(default_factory=utc_now)
    
    def risk_score(self) -> float:
        """Calcula score de risco (severity * likelihood)."""
        severity_scores = {
            RiskSeverity.LOW: 1,
            RiskSeverity.MEDIUM: 2,
            RiskSeverity.HIGH: 3,
            RiskSeverity.CRITICAL: 4
        }
        
        likelihood_scores = {
            RiskLikelihood.RARE: 1,
            RiskLikelihood.UNLIKELY: 2,
            RiskLikelihood.POSSIBLE: 3,
            RiskLikelihood.LIKELY: 4,
            RiskLikelihood.ALMOST_CERTAIN: 5
        }
        
        return severity_scores[self.severity] * likelihood_scores[self.likelihood]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "risk_id": self.risk_id,
            "title": self.title,
            "description": self.description,
            "category": self.category,
            "severity": self.severity.value,
            "likelihood": self.likelihood.value,
            "affected_components": self.affected_components,
            "affected_rules": self.affected_rules,
            "mitigations": self.mitigations,
            "residual_risk": self.residual_risk.value,
            "owner": self.owner,
            "status": self.status,
            "risk_score": self.risk_score(),
            "created_at": self.created_at.isoformat(),
            "last_reviewed": self.last_reviewed.isoformat()
        }

class RiskRegistry:
    """Registo de riscos do sistema."""
    
    def __init__(self):
        self.risks: List[RiskEntry] = []
    
    def add_risk(self, risk: RiskEntry):
        """Adiciona risco ao registo."""
        self.risks.append(risk)
    
    def get_risks_by_severity(self, severity: RiskSeverity) -> List[RiskEntry]:
        """Retorna riscos por severidade."""
        return [r for r in self.risks if r.severity == severity]
    
    def get_high_risk_items(self) -> List[RiskEntry]:
        """Retorna riscos de alta severidade ou probabilidade."""
        return [r for r in self.risks if r.severity in [RiskSeverity.HIGH, RiskSeverity.CRITICAL]]
    
    def get_open_risks(self) -> List[RiskEntry]:
        """Retorna riscos em aberto."""
        return [r for r in self.risks if r.status == "open"]
    
    def to_markdown(self) -> str:
        """Exporta registo em formato Markdown."""
        sections = [
            "# Registo de Riscos",
            "",
            "| ID | Título | Categoria | Severidade | Probabilidade | Score | Status |",
            "|----|--------|-----------|------------|---------------|-------|--------|"
        ]
        
        for risk in self.risks:
            sections.append(
                f"| {risk.risk_id} | {risk.title[:40]}... | {risk.category} | {risk.severity.value} | {risk.likelihood.value} | {risk.risk_score()} | {risk.status} |"
            )
        
        # Estatísticas
        open_risks = len(self.get_open_risks())
        high_risks = len(self.get_high_risk_items())
        
        sections.extend([
            "",
            "## Estatísticas",
            f"- **Total de riscos:** {len(self.risks)}",
            f"- **Riscos em aberto:** {open_risks}",
            f"- **Riscos de alta severidade:** {high_risks}"
        ])
        
        return "\n".join(sections)
