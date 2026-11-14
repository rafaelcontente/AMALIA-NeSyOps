import pytest
from domains.pack import DomainPackLoader
from domains.piloto import create_piloto_pack
from domains.evaluator import DomainEvaluator

@pytest.fixture
def pack_loader():
    return DomainPackLoader()

@pytest.fixture
def piloto_pack():
    return create_piloto_pack()

@pytest.fixture
def evaluator():
    return DomainEvaluator()

# ─── Teste 1: Pack carrega e valida contra core sem alterar core ────────────
def test_pack_loads_and_validates_without_altering_core(pack_loader, piloto_pack):
    """Teste 1: o pack carrega e valida contra os contratos do core sem alterar o core."""
    
    # Contratos do core (imutáveis)
    core_contracts = {
        "version": "1.0.0",
        "required_fields": ["requerente", "estabelecimento"],
        "immutable": True
    }
    
    # Guardar referência original
    original_core_version = core_contracts["version"]
    original_core_required = core_contracts["required_fields"].copy()
    
    # Carregar pack
    pack_loader.load_pack(piloto_pack)
    
    # Verificar que pack está carregado
    loaded_pack = pack_loader.get_pack("piloto", "v0.1")
    assert loaded_pack is not None
    assert loaded_pack.pack_id == "piloto"
    assert loaded_pack.version == "v0.1"
    
    # Validar pack contra core
    validation = loaded_pack.validate_against_core(core_contracts)
    
    # Verificar que validação passou
    assert validation["valid"] is True
    assert len(validation["violations"]) == 0
    
    # Verificar que core não foi alterado
    assert core_contracts["version"] == original_core_version
    assert core_contracts["required_fields"] == original_core_required
    assert core_contracts["immutable"] is True
    
    # Verificar que pack tem todos os componentes
    assert loaded_pack.ontology is not None
    assert loaded_pack.policy is not None
    assert loaded_pack.sources is not None
    assert loaded_pack.golden_set is not None
    assert loaded_pack.templates is not None
    assert loaded_pack.limits is not None

# ─── Teste 2: Concordância com especialistas atinge limiar ──────────────────
def test_agreement_with_experts_meets_threshold(piloto_pack, evaluator):
    """Teste 2: nos casos automáticos, a concordância com os especialistas no golden set atinge o limiar acordado."""
    
    # Função de decisão automática (simula o sistema)
    def automatic_decision_fn(case_data):
        # Extrair dados do caso
        idade = case_data["requerente"]["idade"]
        area = case_data["estabelecimento"]["área_m2"]
        taxa_paga = case_data["licença"]["taxa_paga"]
        risco = case_data["actividade_económica"]["risco"]
        
        # Aplicar regras
        violations = []
        
        if idade < 18:
            violations.append("R-PIL-001")
        if area < 20:
            violations.append("R-PIL-002")
        if not taxa_paga:
            violations.append("R-PIL-003")
        
        # Decisão
        if violations:
            return {
                "decision": "rejected",
                "violated_rules": violations,
                "confidence": 0.95
            }
        else:
            return {
                "decision": "approved",
                "violated_rules": [],
                "confidence": 0.95
            }
    
    # Avaliar pack completo
    result = evaluator.evaluate_pack(piloto_pack, automatic_decision_fn)
    
    # Verificar estrutura do resultado
    assert result["pack_id"] == "piloto"
    assert result["version"] == "v0.1"
    assert result["total_cases"] == 20
    
    # Verificar que não há violações de regras duras
    assert result["hard_rule_violations"] == 0
    
    # Verificar concordância
    agreement = result["agreement"]
    assert agreement["total_cases"] > 0
    assert agreement["agreement_rate"] >= 0.85
    assert agreement["meets_threshold"] is True
    
    # Verificar que maioria dos casos foi decidida automaticamente
    assert result["automatic_decisions"] >= 17  # Pelo menos 17 de 20

# ─── Teste 3: Casos fora de âmbito escalam em vez de decidir ────────────────
def test_out_of_scope_cases_escalate(piloto_pack):
    """Teste 3: os limites do pack estão documentados e os casos fora de âmbito escalam em vez de serem decididos."""
    
    # Verificar que limites estão documentados
    assert len(piloto_pack.limits.in_scope) > 0
    assert len(piloto_pack.limits.out_of_scope) > 0
    assert len(piloto_pack.limits.escalation_criteria) > 0
    
    # Caso dentro do âmbito
    in_scope_case = {
        "id": "CASE-IN-001",
        "requerente": {"idade": 30},
        "estabelecimento": {"área_m2": 100, "tipo": "comércio"},
        "licença": {"tipo": "comércio", "taxa_paga": True},
        "actividade_económica": {"risco": "baixo"}
    }
    
    assert piloto_pack.is_in_scope(in_scope_case) is True
    
    # Caso fora do âmbito: área muito grande
    large_area_case = {
        "id": "CASE-OUT-001",
        "requerente": {"idade": 30},
        "estabelecimento": {"área_m2": 600, "tipo": "comércio"},  # > 500 m²
        "licença": {"tipo": "comércio", "taxa_paga": True},
        "actividade_económica": {"risco": "baixo"}
    }
    
    assert piloto_pack.is_in_scope(large_area_case) is False
    
    # Caso fora do âmbito: risco elevado
    high_risk_case = {
        "id": "CASE-OUT-002",
        "requerente": {"idade": 30},
        "estabelecimento": {"área_m2": 100, "tipo": "comércio"},
        "licença": {"tipo": "comércio", "taxa_paga": True},
        "actividade_económica": {"risco": "elevado"}  # risco elevado
    }
    
    assert piloto_pack.is_in_scope(high_risk_case) is False
    
    # Caso fora do âmbito: tipo industrial
    industrial_case = {
        "id": "CASE-OUT-003",
        "requerente": {"idade": 30},
        "estabelecimento": {"área_m2": 100, "tipo": "industrial"},  # tipo industrial
        "licença": {"tipo": "industrial", "taxa_paga": True},
        "actividade_económica": {"risco": "baixo"}
    }
    
    assert piloto_pack.is_in_scope(industrial_case) is False
    
    # Verificar que casos fora de âmbito estão documentados
    assert "Licenciamento industrial" in piloto_pack.limits.out_of_scope
    assert "Estabelecimentos com área superior a 500 m²" in piloto_pack.limits.out_of_scope
    assert "Actividades de risco elevado" in piloto_pack.limits.out_of_scope
