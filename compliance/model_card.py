"""
Model cards e fichas de dados gerados a partir de metadados reais do sistema.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field, ConfigDict
import json

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

class ModelCard(BaseModel):
    """Model card para um modelo ou componente do sistema."""
    model_config = ConfigDict(frozen=True)
    
    model_name: str
    version: str
    description: str
    
    # Intended use
    intended_use: str
    intended_users: List[str]
    out_of_scope_use_cases: List[str]
    
    # Performance
    metrics: Dict[str, float] = Field(default_factory=dict)
    evaluation_data: str = ""
    
    # Limitations
    limitations: List[str] = Field(default_factory=list)
    bias_considerations: List[str] = Field(default_factory=list)
    
    # Training
    training_data: str = ""
    training_methodology: str = ""
    
    # Ethical considerations
    ethical_considerations: List[str] = Field(default_factory=list)
    
    # Metadata
    created_at: datetime = Field(default_factory=utc_now)
    last_updated: datetime = Field(default_factory=utc_now)
    
    def to_markdown(self) -> str:
        """Exporta model card em formato Markdown."""
        sections = [
            f"# Model Card: {self.model_name} {self.version}",
            f"",
            f"## Descrição",
            f"{self.description}",
            f"",
            f"## Uso Previsto",
            f"**Uso:** {self.intended_use}",
            f"",
            f"**Utilizadores:** {', '.join(self.intended_users)}",
            f"",
            f"**Casos fora do âmbito:**",
        ]
        
        for case in self.out_of_scope_use_cases:
            sections.append(f"- {case}")
        
        sections.extend([
            f"",
            f"## Desempenho",
        ])
        
        if self.metrics:
            sections.append("**Métricas:**")
            for metric, value in self.metrics.items():
                sections.append(f"- {metric}: {value:.3f}")
        else:
            sections.append("Métricas ainda não avaliadas.")
        
        sections.extend([
            f"",
            f"**Dados de avaliação:** {self.evaluation_data or 'Não especificado'}",
            f"",
            f"## Limitações",
        ])
        
        if self.limitations:
            for limitation in self.limitations:
                sections.append(f"- {limitation}")
        else:
            sections.append("Nenhuma limitação conhecida.")
        
        sections.extend([
            f"",
            f"## Considerações de Viés",
        ])
        
        if self.bias_considerations:
            for bias in self.bias_considerations:
                sections.append(f"- {bias}")
        else:
            sections.append("Viés ainda não avaliado.")
        
        sections.extend([
            f"",
            f"## Formação",
            f"**Dados:** {self.training_data or 'Não especificado'}",
            f"",
            f"**Metodologia:** {self.training_methodology or 'Não especificado'}",
            f"",
            f"## Considerações Éticas",
        ])
        
        if self.ethical_considerations:
            for ethical in self.ethical_considerations:
                sections.append(f"- {ethical}")
        else:
            sections.append("Considerações éticas ainda não documentadas.")
        
        sections.extend([
            f"",
            f"## Metadados",
            f"**Criado em:** {self.created_at.isoformat()}",
            f"**Última atualização:** {self.last_updated.isoformat()}",
        ])
        
        return "\n".join(sections)

class DataSheet(BaseModel):
    """Ficha de dados para um dataset."""
    model_config = ConfigDict(frozen=True)
    
    name: str
    version: str
    description: str
    
    # Motivation
    purpose: str
    creators: List[str]
    
    # Composition
    instances_count: int
    features: List[str] = Field(default_factory=list)
    missing_values: bool = False
    confidential_data: bool = False
    personal_data: bool = False
    
    # Collection
    collection_method: str = ""
    collection_timeframe: str = ""
    
    # Preprocessing
    preprocessing_steps: List[str] = Field(default_factory=list)
    
    # Uses
    existing_uses: List[str] = Field(default_factory=list)
    other_uses: List[str] = Field(default_factory=list)
    
    # Distribution
    distribution_method: str = ""
    license: str = ""
    
    # Maintenance
    maintainers: List[str] = Field(default_factory=list)
    updates: str = ""
    
    created_at: datetime = Field(default_factory=utc_now)
    
    def to_markdown(self) -> str:
        """Exporta ficha de dados em formato Markdown."""
        sections = [
            f"# Ficha de Dados: {self.name} v{self.version}",
            f"",
            f"## Descrição",
            f"{self.description}",
            f"",
            f"## Motivação",
            f"**Propósito:** {self.purpose}",
            f"",
            f"**Criadores:** {', '.join(self.creators)}",
            f"",
            f"## Composição",
            f"**Instâncias:** {self.instances_count}",
            f"",
            f"**Características:**",
        ]
        
        for feature in self.features:
            sections.append(f"- {feature}")
        
        sections.extend([
            f"",
            f"**Valores em falta:** {'Sim' if self.missing_values else 'Não'}",
            f"",
            f"**Dados confidenciais:** {'Sim' if self.confidential_data else 'Não'}",
            f"",
            f"**Dados pessoais:** {'Sim' if self.personal_data else 'Não'}",
            f"",
            f"## Recolha",
            f"**Método:** {self.collection_method or 'Não especificado'}",
            f"",
            f"**Período:** {self.collection_timeframe or 'Não especificado'}",
            f"",
            f"## Pré-processamento",
        ])
        
        if self.preprocessing_steps:
            for step in self.preprocessing_steps:
                sections.append(f"- {step}")
        else:
            sections.append("Nenhum pré-processamento aplicado.")
        
        sections.extend([
            f"",
            f"## Usos",
            f"**Usos existentes:**",
        ])
        
        for use in self.existing_uses:
            sections.append(f"- {use}")
        
        sections.extend([
            f"",
            f"**Outros usos possíveis:**",
        ])
        
        for use in self.other_uses:
            sections.append(f"- {use}")
        
        sections.extend([
            f"",
            f"## Distribuição",
            f"**Método:** {self.distribution_method or 'Não especificado'}",
            f"",
            f"**Licença:** {self.license or 'Não especificado'}",
            f"",
            f"## Manutenção",
            f"**Responsáveis:** {', '.join(self.maintainers) if self.maintainers else 'Não especificado'}",
            f"",
            f"**Atualizações:** {self.updates or 'Não especificado'}",
            f"",
            f"## Metadados",
            f"**Criado em:** {self.created_at.isoformat()}",
        ])
        
        return "\n".join(sections)

class ModelCardGenerator:
    """Gera model cards a partir de metadados do sistema."""
    
    def generate_system_card(self, system_metadata: Dict[str, Any]) -> ModelCard:
        """Gera model card para o sistema AMALIA."""
        return ModelCard(
            model_name=system_metadata.get("name", "AMALIA"),
            version=system_metadata.get("version", "v0.3"),
            description=system_metadata.get("description", "Sistema neuro-simbólico para decisões administrativas"),
            intended_use=system_metadata.get("intended_use", "Apoio à decisão em procedimentos administrativos"),
            intended_users=system_metadata.get("intended_users", ["Funcionários públicos", "Juristas", "Auditores"]),
            out_of_scope_use_cases=system_metadata.get("out_of_scope", [
                "Decisões judiciais",
                "Substituição de julgamento humano em casos complexos",
                "Uso fora do domínio administrativo"
            ]),
            metrics=system_metadata.get("metrics", {}),
            evaluation_data=system_metadata.get("evaluation_data", ""),
            limitations=system_metadata.get("limitations", [
                "Dependente da qualidade dos dados de entrada",
                "Regras devem ser mantidas atualizadas"
            ]),
            bias_considerations=system_metadata.get("bias", []),
            training_data=system_metadata.get("training_data", ""),
            training_methodology=system_metadata.get("methodology", ""),
            ethical_considerations=system_metadata.get("ethical", [
                "Transparência nas decisões",
                "Direito à explicação",
                "Supervisão humana em casos de alto risco"
            ])
        )
