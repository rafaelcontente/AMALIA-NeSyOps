"""
Checklist de validação humana por jurista ou DPO.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field, ConfigDict

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

class ChecklistItem(BaseModel):
    """Item da checklist."""
    model_config = ConfigDict(frozen=True)
    
    item_id: str
    category: str  # "legal", "technical", "ethical", "operational"
    requirement: str
    checked: bool = False
    notes: str = ""
    checked_by: Optional[str] = None
    checked_at: Optional[datetime] = None

class ComplianceChecklist(BaseModel):
    """Checklist de conformidade."""
    model_config = ConfigDict(frozen=False)
    
    checklist_id: str
    system_version: str
    domain: str
    
    items: List[ChecklistItem] = Field(default_factory=list)
    
    reviewer_name: Optional[str] = None
    reviewer_role: Optional[str] = None  # "jurist", "dpo", "auditor"
    review_date: Optional[datetime] = None
    signature: Optional[str] = None  # Hash ou ID digital
    
    created_at: datetime = Field(default_factory=utc_now)
    
    def add_item(self, item: ChecklistItem):
        """Adiciona item à checklist."""
        self.items.append(item)
    
    def check_item(self, item_id: str, checked_by: str, notes: str = "") -> bool:
        """Marca item como verificado."""
        for i, item in enumerate(self.items):
            if item.item_id == item_id:
                updated_item = ChecklistItem(
                    item_id=item.item_id,
                    category=item.category,
                    requirement=item.requirement,
                    checked=True,
                    notes=notes,
                    checked_by=checked_by,
                    checked_at=utc_now()
                )
                self.items[i] = updated_item
                return True
        return False
    
    def sign(self, reviewer_name: str, reviewer_role: str, signature: str):
        """Assina a checklist."""
        self.reviewer_name = reviewer_name
        self.reviewer_role = reviewer_role
        self.review_date = utc_now()
        self.signature = signature
    
    def is_complete(self) -> bool:
        """Verifica se todos os itens foram verificados."""
        return all(item.checked for item in self.items)
    
    def completion_rate(self) -> float:
        """Calcula taxa de conclusão."""
        if not self.items:
            return 0.0
        checked = sum(1 for item in self.items if item.checked)
        return checked / len(self.items)
    
    def to_markdown(self) -> str:
        """Exporta checklist em formato Markdown."""
        sections = [
            f"# Checklist de Conformidade: {self.checklist_id}",
            f"",
            f"**Versão do sistema:** {self.system_version}",
            f"",
            f"**Domínio:** {self.domain}",
            f"",
            f"## Itens",
            "",
            "| ID | Categoria | Requisito | Verificado | Notas | Verificado por |",
            "|----|-----------|-----------|------------|-------|----------------|"
        ]
        
        for item in self.items:
            checked = "✅" if item.checked else "❌"
            checked_by = item.checked_by or "N/A"
            sections.append(
                f"| {item.item_id} | {item.category} | {item.requirement[:40]}... | {checked} | {item.notes[:30]} | {checked_by} |"
            )
        
        sections.extend([
            "",
            "## Validação",
            f"**Taxa de conclusão:** {self.completion_rate():.1%}",
            f"",
            f"**Revisor:** {self.reviewer_name or 'Não assinado'}",
            f"",
            f"**Função:** {self.reviewer_role or 'N/A'}",
            f"",
            f"**Data de revisão:** {self.review_date.isoformat() if self.review_date else 'N/A'}",
            f"",
            f"**Assinatura:** {self.signature or 'Não assinado'}"
        ])
        
        return "\n".join(sections)

class ChecklistGenerator:
    """Gera checklists de conformidade."""
    
    def generate_standard_checklist(self, checklist_id: str, system_version: str, 
                                    domain: str) -> ComplianceChecklist:
        """Gera checklist padrão com itens comuns."""
        checklist = ComplianceChecklist(
            checklist_id=checklist_id,
            system_version=system_version,
            domain=domain
        )
        
        # Itens legais
        checklist.add_item(ChecklistItem(
            item_id="LEGAL-001",
            category="legal",
            requirement="Sistema cumpre requisitos do EU AI Act para sistemas de alto risco"
        ))
        
        checklist.add_item(ChecklistItem(
            item_id="LEGAL-002",
            category="legal",
            requirement="Decisões automatizadas têm intervenção humana quando necessário (RGPD Art. 22)"
        ))
        
        checklist.add_item(ChecklistItem(
            item_id="LEGAL-003",
            category="legal",
            requirement="Direito à explicação está implementado"
        ))
        
        # Itens técnicos
        checklist.add_item(ChecklistItem(
            item_id="TECH-001",
            category="technical",
            requirement="Matriz de rastreabilidade está completa (requisito → regra → teste)"
        ))
        
        checklist.add_item(ChecklistItem(
            item_id="TECH-002",
            category="technical",
            requirement="Registo de auditoria está ativo e imutável"
        ))
        
        checklist.add_item(ChecklistItem(
            item_id="TECH-003",
            category="technical",
            requirement="Kill switch está implementado e testado"
        ))
        
        # Itens éticos
        checklist.add_item(ChecklistItem(
            item_id="ETH-001",
            category="ethical",
            requirement="Avaliação de viés foi realizada"
        ))
        
        checklist.add_item(ChecklistItem(
            item_id="ETH-002",
            category="ethical",
            requirement="Transparência nas decisões está garantida"
        ))
        
        # Itens operacionais
        checklist.add_item(ChecklistItem(
            item_id="OPS-001",
            category="operational",
            requirement="Documentação técnica está atualizada"
        ))
        
        checklist.add_item(ChecklistItem(
            item_id="OPS-002",
            category="operational",
            requirement="Plano de resposta a incidentes está definido"
        ))
        
        return checklist
