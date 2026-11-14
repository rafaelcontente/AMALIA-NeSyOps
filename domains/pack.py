"""Pacote de domínio: empacota ontologia, regras, fontes legais e golden set."""
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timezone
from pydantic import BaseModel, Field
import json

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

class DomainOntology(BaseModel):
    """Ontologia do domínio (entidades, relações, atributos)."""
    entities: List[str]
    relationships: List[Dict[str, str]]
    attributes: Dict[str, List[str]]

class DomainPolicy(BaseModel):
    """Conjunto de regras do domínio."""
    rules: List[Dict[str, Any]]
    hard_rules: List[str]  # IDs de regras duras
    soft_rules: List[str]  # IDs de regras suaves

class DomainSources(BaseModel):
    """Fontes legais e normativas do domínio."""
    legal_sources: List[Dict[str, str]]
    normative_texts: List[Dict[str, str]]
    precedents: List[Dict[str, Any]]

class DomainGoldenSet(BaseModel):
    """Golden set de decisões anotadas por especialistas."""
    cases: List[Dict[str, Any]]
    expert_decisions: Dict[str, Dict[str, Any]]
    agreement_threshold: float = 0.85

class DomainTemplates(BaseModel):
    """Templates de explicação específicos do domínio."""
    approval_template: str
    rejection_template: str
    escalation_template: str

class DomainLimits(BaseModel):
    """Limites e âmbito do domínio."""
    in_scope: List[str]
    out_of_scope: List[str]
    escalation_criteria: List[str]
    binary_decisions: bool = True
    ordinal_decisions: bool = False

class DomainPack(BaseModel):
    """Pacote completo de domínio."""
    pack_id: str
    version: str
    name: str
    description: str
    
    ontology: DomainOntology
    policy: DomainPolicy
    sources: DomainSources
    golden_set: DomainGoldenSet
    templates: DomainTemplates
    limits: DomainLimits
    
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
    
    def is_in_scope(self, case_data: Dict[str, Any]) -> bool:
        """
        Verifica se um caso está dentro do âmbito do domínio.
        
        Args:
            case_data: Dados do caso a avaliar
        
        Returns:
            True se está dentro do âmbito, False se deve escalar
        """
        # Verificar critérios de escalonamento
        for criterion in self.limits.escalation_criteria:
            if self._matches_criterion(case_data, criterion):
                return False
        
        return True
    
    def _matches_criterion(self, case_data: Dict[str, Any], criterion: str) -> bool:
        """Verifica se caso corresponde a critério de escalonamento."""
        try:
            # Parse simples de critério
            if ">" in criterion:
                parts = criterion.split(">")
                field_path = parts[0].strip()
                threshold = float(parts[1].strip())
                value = self._get_nested_value(case_data, field_path)
                if value is not None:
                    return float(value) > threshold
            elif "==" in criterion:
                parts = criterion.split("==")
                field_path = parts[0].strip()
                expected_value = parts[1].strip().strip("'\"")
                value = self._get_nested_value(case_data, field_path)
                if value is not None:
                    return str(value) == expected_value
        except Exception:
            pass
        
        return False
    
    def _get_nested_value(self, data: Dict[str, Any], field_path: str) -> Any:
        """
        Obtém valor de campo aninhado.
        
        Procura o campo em múltiplos níveis:
        1. Acesso directo: data[field_path]
        2. Caminho completo: data["entidade"][field_path]
        3. Busca profunda em todas as sub-entidades
        """
        # 1. Tentar acesso directo
        if field_path in data:
            return data[field_path]
        
        # 2. Tentar caminho com ponto (ex: "estabelecimento.área_m2")
        if "." in field_path:
            parts = field_path.split(".")
            current = data
            for part in parts:
                if isinstance(current, dict) and part in current:
                    current = current[part]
                else:
                    break
            else:
                return current
        
        # 3. Busca profunda em todas as sub-entidades
        for key, value in data.items():
            if isinstance(value, dict):
                if field_path in value:
                    return value[field_path]
                # Busca recursiva
                result = self._get_nested_value(value, field_path)
                if result is not None:
                    return result
        
        return None
    
    def validate_against_core(self, core_contracts: Dict[str, Any]) -> Dict[str, Any]:
        """
        Valida o pack contra contratos do core sem alterar o core.
        
        Args:
            core_contracts: Contratos do core (imutáveis)
        
        Returns:
            Resultado da validação
        """
        validation_result = {
            "pack_id": self.pack_id,
            "version": self.version,
            "valid": True,
            "violations": [],
            "warnings": []
        }
        
        # Verificar que regras duras estão definidas
        if not self.policy.hard_rules:
            validation_result["warnings"].append("Nenhuma regra dura definida")
        
        # Verificar que golden set tem casos
        if not self.golden_set.cases:
            validation_result["violations"].append("Golden set vazio")
            validation_result["valid"] = False
        
        # Verificar que limites estão documentados
        if not self.limits.out_of_scope:
            validation_result["warnings"].append("Limites fora de âmbito não documentados")
        
        # Verificar que templates estão definidos
        if not self.templates.approval_template:
            validation_result["violations"].append("Template de aprovação não definido")
            validation_result["valid"] = False
        
        # Verificar conformidade com contratos do core
        if "required_fields" in core_contracts:
            for field in core_contracts["required_fields"]:
                if field not in self.ontology.entities:
                    validation_result["violations"].append(
                        f"Campo obrigatório do core não está na ontologia: {field}"
                    )
                    validation_result["valid"] = False
        
        return validation_result

class DomainPackLoader:
    """Carregador de pacotes de domínio."""
    
    def __init__(self):
        self.packs: Dict[str, DomainPack] = {}
    
    def load_pack(self, pack: DomainPack):
        """Carrega um pacote de domínio."""
        key = f"{pack.pack_id}_{pack.version}"
        self.packs[key] = pack
    
    def get_pack(self, pack_id: str, version: str = "latest") -> Optional[DomainPack]:
        """Retorna um pacote de domínio."""
        if version == "latest":
            # Retornar versão mais recente
            matching_packs = [
                p for p in self.packs.values() if p.pack_id == pack_id
            ]
            if not matching_packs:
                return None
            return max(matching_packs, key=lambda p: p.version)
        
        key = f"{pack_id}_{version}"
        return self.packs.get(key)
    
    def list_packs(self) -> List[DomainPack]:
        """Lista todos os pacotes carregados."""
        return list(self.packs.values())
