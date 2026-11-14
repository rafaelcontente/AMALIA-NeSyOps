"""
Mapeamento para frameworks regulatórios: EU AI Act, RGPD, ISO 42001, NIST AI RMF.
"""
from typing import Dict, Any, List
from datetime import datetime, timezone

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

class FrameworkMapping:
    """Mapeamento para um framework regulatório específico."""
    
    def __init__(self, framework_name: str, version: str):
        self.framework_name = framework_name
        self.version = version
        self.requirements: Dict[str, Dict[str, Any]] = {}
        self.coverage: Dict[str, List[str]] = {}  # requirement_id -> [rule_ids]
    
    def add_requirement(self, requirement_id: str, description: str, 
                       article: str, risk_level: str):
        """Adiciona requisito do framework."""
        self.requirements[requirement_id] = {
            "description": description,
            "article": article,
            "risk_level": risk_level,
            "covered": False
        }
        self.coverage[requirement_id] = []
    
    def map_rule_to_requirement(self, requirement_id: str, rule_id: str):
        """Mapeia regra do sistema para requisito do framework."""
        if requirement_id in self.coverage:
            self.coverage[requirement_id].append(rule_id)
            self.requirements[requirement_id]["covered"] = True
    
    def get_uncovered_requirements(self) -> List[str]:
        """Retorna requisitos não cobertos por regras."""
        return [req_id for req_id, req in self.requirements.items() if not req["covered"]]
    
    def get_coverage_rate(self) -> float:
        """Calcula taxa de cobertura do framework."""
        if not self.requirements:
            return 0.0
        
        covered = sum(1 for req in self.requirements.values() if req["covered"])
        return covered / len(self.requirements)
    
    def to_markdown(self) -> str:
        """Exporta mapeamento em formato Markdown."""
        sections = [
            f"# Mapeamento: {self.framework_name} v{self.version}",
            "",
            "| ID | Artigo | Descrição | Nível de Risco | Coberto | Regras |",
            "|----|--------|-----------|----------------|---------|--------|"
        ]
        
        for req_id, req in self.requirements.items():
            rules = ", ".join(self.coverage.get(req_id, [])) or "Nenhuma"
            covered = "✅" if req["covered"] else "❌"
            
            sections.append(
                f"| {req_id} | {req['article']} | {req['description'][:50]}... | {req['risk_level']} | {covered} | {rules} |"
            )
        
        # Estatísticas
        coverage_rate = self.get_coverage_rate()
        uncovered = self.get_uncovered_requirements()
        
        sections.extend([
            "",
            "## Estatísticas",
            f"- **Taxa de cobertura:** {coverage_rate:.1%}",
            f"- **Requisitos não cobertos:** {len(uncovered)}"
        ])
        
        if uncovered:
            sections.append("")
            sections.append("**Requisitos não cobertos:**")
            for req_id in uncovered:
                sections.append(f"- {req_id}")
        
        return "\n".join(sections)

class FrameworkMapper:
    """Gere mapeamentos para múltiplos frameworks."""
    
    def __init__(self):
        self.mappings: Dict[str, FrameworkMapping] = {}
    
    def create_eu_ai_act_mapping(self) -> FrameworkMapping:
        """Cria mapeamento para EU AI Act."""
        mapping = FrameworkMapping("EU AI Act", "2024")
        
        # Exemplos de requisitos do EU AI Act
        mapping.add_requirement(
            "EU-AI-001",
            "Sistema de IA de alto risco deve ter sistema de gestão de riscos",
            "Artigo 9",
            "high"
        )
        
        mapping.add_requirement(
            "EU-AI-002",
            "Dados de treino devem satisfazer critérios de qualidade",
            "Artigo 10",
            "high"
        )
        
        mapping.add_requirement(
            "EU-AI-003",
            "Documentação técnica deve ser mantida",
            "Artigo 11",
            "high"
        )
        
        mapping.add_requirement(
            "EU-AI-004",
            "Registo de atividades (logging) deve ser mantido",
            "Artigo 12",
            "medium"
        )
        
        mapping.add_requirement(
            "EU-AI-005",
            "Transparência e informação aos utilizadores",
            "Artigo 13",
            "high"
        )
        
        self.mappings["eu_ai_act"] = mapping
        return mapping
    
    def create_gdpr_mapping(self) -> FrameworkMapping:
        """Cria mapeamento para RGPD."""
        mapping = FrameworkMapping("RGPD", "2016/679")
        
        mapping.add_requirement(
            "RGPD-001",
            "Decisões automatizadas com efeitos significativos requerem intervenção humana",
            "Artigo 22",
            "high"
        )
        
        mapping.add_requirement(
            "RGPD-002",
            "Direito à explicação de decisões automatizadas",
            "Artigo 13-15",
            "high"
        )
        
        mapping.add_requirement(
            "RGPD-003",
            "Minimização de dados pessoais",
            "Artigo 5",
            "high"
        )
        
        mapping.add_requirement(
            "RGPD-004",
            "Direito ao esquecimento",
            "Artigo 17",
            "medium"
        )
        
        self.mappings["gdpr"] = mapping
        return mapping
    
    def get_mapping(self, framework_name: str) -> FrameworkMapping:
        """Retorna mapeamento por nome do framework."""
        return self.mappings.get(framework_name)
