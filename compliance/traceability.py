"""
Matriz de rastreabilidade: requisito → regra → teste → registo.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field, ConfigDict

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

class TraceabilityEntry(BaseModel):
    """Entrada na matriz de rastreabilidade."""
    model_config = ConfigDict(frozen=True)
    
    requirement_id: str  # Ex: "REQ-001"
    requirement_text: str
    source_norm: str  # Ex: "Lei n.º 123/2024, art. 45.º"
    
    rule_id: str  # Ex: "R-012"
    rule_version: str
    rule_expression: str
    
    test_id: str  # Ex: "T-044"
    test_description: str
    last_execution: Optional[datetime] = None
    last_result: Optional[str] = None  # "passed", "failed"
    
    audit_log_id: Optional[str] = None  # Ligação ao audit ledger
    
    status: str = "complete"  # "complete", "missing_test", "missing_approval"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "requirement_id": self.requirement_id,
            "requirement_text": self.requirement_text,
            "source_norm": self.source_norm,
            "rule_id": self.rule_id,
            "rule_version": self.rule_version,
            "rule_expression": self.rule_expression,
            "test_id": self.test_id,
            "test_description": self.test_description,
            "last_execution": self.last_execution.isoformat() if self.last_execution else None,
            "last_result": self.last_result,
            "audit_log_id": self.audit_log_id,
            "status": self.status
        }

class TraceabilityMatrix:
    """Matriz de rastreabilidade completa."""
    
    def __init__(self):
        self.entries: List[TraceabilityEntry] = []
    
    def add_entry(self, entry: TraceabilityEntry):
        """Adiciona entrada à matriz."""
        self.entries.append(entry)
    
    def get_entry_by_rule(self, rule_id: str) -> Optional[TraceabilityEntry]:
        """Retorna entrada por ID de regra."""
        for entry in self.entries:
            if entry.rule_id == rule_id:
                return entry
        return None
    
    def get_missing_tests(self) -> List[TraceabilityEntry]:
        """Retorna regras sem testes associados."""
        return [e for e in self.entries if e.status == "missing_test"]
    
    def get_missing_approvals(self) -> List[TraceabilityEntry]:
        """Retorna regras sem aprovação."""
        return [e for e in self.entries if e.status == "missing_approval"]
    
    def validate_completeness(self) -> Dict[str, Any]:
        """Valida completude da matriz."""
        total = len(self.entries)
        complete = len([e for e in self.entries if e.status == "complete"])
        missing_tests = len(self.get_missing_tests())
        missing_approvals = len(self.get_missing_approvals())
        
        return {
            "total_rules": total,
            "complete": complete,
            "missing_tests": missing_tests,
            "missing_approvals": missing_approvals,
            "completeness_rate": complete / total if total > 0 else 0.0
        }
    
    def to_markdown(self) -> str:
        """Exporta matriz em formato Markdown."""
        sections = [
            "# Matriz de Rastreabilidade",
            "",
            "| Requisito | Norma | Regra | Teste | Última Execução | Resultado | Status |",
            "|-----------|-------|-------|-------|-----------------|-----------|--------|"
        ]
        
        for entry in self.entries:
            last_exec = entry.last_execution.strftime("%Y-%m-%d") if entry.last_execution else "N/A"
            last_result = entry.last_result or "N/A"
            
            sections.append(
                f"| {entry.requirement_id} | {entry.source_norm[:30]}... | {entry.rule_id} | {entry.test_id} | {last_exec} | {last_result} | {entry.status} |"
            )
        
        # Estatísticas
        stats = self.validate_completeness()
        sections.extend([
            "",
            "## Estatísticas",
            f"- **Total de regras:** {stats['total_rules']}",
            f"- **Completas:** {stats['complete']}",
            f"- **Sem teste:** {stats['missing_tests']}",
            f"- **Sem aprovação:** {stats['missing_approvals']}",
            f"- **Taxa de completude:** {stats['completeness_rate']:.1%}"
        ])
        
        return "\n".join(sections)

class TraceabilityBuilder:
    """Constrói matriz de rastreabilidade a partir de dados do sistema."""
    
    def build_from_rules(self, rules: List[Dict], tests: List[Dict], 
                         audit_logs: List[Dict] = None) -> TraceabilityMatrix:
        """
        Constrói matriz a partir de regras, testes e logs de auditoria.
        """
        matrix = TraceabilityMatrix()
        
        # Indexar testes por rule_id
        tests_by_rule = {t.get("rule_id"): t for t in tests}
        
        # Indexar logs por rule_id
        logs_by_rule = {}
        if audit_logs:
            for log in audit_logs:
                rule_id = log.get("rule_id")
                if rule_id:
                    logs_by_rule[rule_id] = log
        
        # Construir entradas
        for rule in rules:
            rule_id = rule.get("id")
            
            # Verificar se tem teste
            test = tests_by_rule.get(rule_id)
            test_id = test.get("id") if test else "SEM_TESTE"
            test_desc = test.get("description", "") if test else ""
            
            # Verificar se tem log de auditoria
            log = logs_by_rule.get(rule_id)
            last_exec = None
            last_result = None
            audit_log_id = None
            
            if log:
                last_exec_str = log.get("last_execution")
                if last_exec_str:
                    last_exec = datetime.fromisoformat(last_exec_str)
                last_result = log.get("last_result")
                audit_log_id = log.get("audit_log_id")
            
            # Determinar status
            if test_id == "SEM_TESTE":
                status = "missing_test"
            elif not rule.get("approved", False):
                status = "missing_approval"
            else:
                status = "complete"
            
            entry = TraceabilityEntry(
                requirement_id=rule.get("requirement_id", "REQ-???"),
                requirement_text=rule.get("requirement_text", ""),
                source_norm=rule.get("source_norm", ""),
                rule_id=rule_id,
                rule_version=rule.get("version", ""),
                rule_expression=rule.get("expression", ""),
                test_id=test_id,
                test_description=test_desc,
                last_execution=last_exec,
                last_result=last_result,
                audit_log_id=audit_log_id,
                status=status
            )
            
            matrix.add_entry(entry)
        
        return matrix
