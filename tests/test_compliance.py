import pytest
from datetime import datetime, timezone
from compliance.model_card import ModelCard, ModelCardGenerator
from compliance.traceability import TraceabilityMatrix, TraceabilityEntry, TraceabilityBuilder
from compliance.risk_registry import RiskRegistry, RiskEntry, RiskSeverity, RiskLikelihood
from compliance.framework_mapping import FrameworkMapper
from compliance.checklist import ComplianceChecklist, ChecklistGenerator

@pytest.fixture
def model_card_generator():
    return ModelCardGenerator()

@pytest.fixture
def traceability_builder():
    return TraceabilityBuilder()

@pytest.fixture
def framework_mapper():
    return FrameworkMapper()

@pytest.fixture
def checklist_generator():
    return ChecklistGenerator()

# ─── Teste 1: Matriz de rastreabilidade completa ────────────────────────────
def test_traceability_matrix_completeness(traceability_builder):
    """Teste 1: cada regra ativa aparece na matriz com norma de origem, teste e última execução."""
    
    # Dados simulados do sistema
    rules = [
        {
            "id": "R-012",
            "version": "1.0.0",
            "expression": "idade >= 18",
            "requirement_id": "REQ-001",
            "requirement_text": "Candidato deve ser maior de idade",
            "source_norm": "Lei n.º 123/2024, art. 45.º",
            "approved": True
        },
        {
            "id": "R-020",
            "version": "1.0.0",
            "expression": "rendimento > 1000",
            "requirement_id": "REQ-002",
            "requirement_text": "Rendimento mínimo para elegibilidade",
            "source_norm": "Decreto-Lei n.º 456/2023, art. 12.º",
            "approved": True
        },
        {
            "id": "R-031",
            "version": "1.0.0",
            "expression": "residencia_meses >= 12",
            "requirement_id": "REQ-003",
            "requirement_text": "Residência mínima de 12 meses",
            "source_norm": "Lei n.º 789/2022, art. 8.º",
            "approved": False  # Sem aprovação
        }
    ]
    
    tests = [
        {
            "id": "T-044",
            "rule_id": "R-012",
            "description": "Teste de maioridade"
        },
        {
            "id": "T-045",
            "rule_id": "R-020",
            "description": "Teste de rendimento mínimo"
        }
        # R-031 não tem teste
    ]
    
    audit_logs = [
        {
            "rule_id": "R-012",
            "last_execution": "2026-11-10T14:30:00",
            "last_result": "passed",
            "audit_log_id": "LOG-001"
        },
        {
            "rule_id": "R-020",
            "last_execution": "2026-11-11T09:15:00",
            "last_result": "passed",
            "audit_log_id": "LOG-002"
        }
    ]
    
    # Construir matriz
    matrix = traceability_builder.build_from_rules(rules, tests, audit_logs)
    
    # Verificar que todas as regras estão na matriz
    assert len(matrix.entries) == 3
    
    # Verificar R-012: completa
    entry_r012 = matrix.get_entry_by_rule("R-012")
    assert entry_r012 is not None
    assert entry_r012.source_norm == "Lei n.º 123/2024, art. 45.º"
    assert entry_r012.test_id == "T-044"
    assert entry_r012.last_execution is not None
    assert entry_r012.last_result == "passed"
    assert entry_r012.status == "complete"
    
    # Verificar R-020: completa
    entry_r020 = matrix.get_entry_by_rule("R-020")
    assert entry_r020 is not None
    assert entry_r020.test_id == "T-045"
    assert entry_r020.status == "complete"
    
    # Verificar R-031: sem teste e sem aprovação
    entry_r031 = matrix.get_entry_by_rule("R-031")
    assert entry_r031 is not None
    assert entry_r031.test_id == "SEM_TESTE"
    assert entry_r031.status == "missing_test"
    
    # Verificar validação de completude
    stats = matrix.validate_completeness()
    assert stats["total_rules"] == 3
    assert stats["complete"] == 2
    assert stats["missing_tests"] == 1
    assert stats["missing_approvals"] == 0  # R-031 é missing_test, não missing_approval
    
    # Verificar que regras sem ligação são apontadas
    missing_tests = matrix.get_missing_tests()
    assert len(missing_tests) == 1
    assert missing_tests[0].rule_id == "R-031"

# ─── Teste 2: Pacote gerado a partir de tag é reproduzível ──────────────────
def test_compliance_package_reproducibility(model_card_generator, framework_mapper):
    """Teste 2: o pacote é gerado automaticamente a partir de uma versão marcada e é reproduzível."""
    
    # Metadados do sistema para versão v0.3
    system_metadata = {
        "name": "AMALIA",
        "version": "v0.3",
        "description": "Sistema neuro-simbólico para decisões administrativas",
        "intended_use": "Apoio à decisão em procedimentos administrativos",
        "intended_users": ["Funcionários públicos", "Juristas"],
        "out_of_scope": ["Decisões judiciais"],
        "metrics": {"accuracy": 0.95, "precision": 0.93},
        "evaluation_data": "Golden set v1.2",
        "limitations": ["Dependente da qualidade dos dados"],
        "bias": ["Avaliação de viés em curso"],
        "training_data": "Corpus jurídico pt-PT",
        "methodology": "Fine-tuning + RAG",
        "ethical": ["Transparência", "Supervisão humana"]
    }
    
    # Gerar pacote para v0.3 (primeira vez)
    model_card_1 = model_card_generator.generate_system_card(system_metadata)
    
    # Criar mapeamento EU AI Act
    eu_ai_act = framework_mapper.create_eu_ai_act_mapping()
    eu_ai_act.map_rule_to_requirement("EU-AI-001", "R-012")
    eu_ai_act.map_rule_to_requirement("EU-AI-002", "R-020")
    
    # Gerar pacote para v0.3 (segunda vez - deve ser idêntico)
    model_card_2 = model_card_generator.generate_system_card(system_metadata)
    
    # Verificar reprodutibilidade (exceto timestamps)
    assert model_card_1.model_name == model_card_2.model_name
    assert model_card_1.version == model_card_2.version
    assert model_card_1.description == model_card_2.description
    assert model_card_1.intended_use == model_card_2.intended_use
    assert model_card_1.metrics == model_card_2.metrics
    
    # Verificar que o model card pode ser exportado
    markdown = model_card_1.to_markdown()
    assert "# Model Card: AMALIA v0.3" in markdown
    assert "v0.3" in markdown
    assert "accuracy" in markdown
    
    # Verificar mapeamento do framework
    assert eu_ai_act.get_coverage_rate() > 0
    assert "EU-AI-001" in eu_ai_act.coverage
    assert "R-012" in eu_ai_act.coverage["EU-AI-001"]

# ─── Teste 3: Jurista/DPO revê e assina checklist ──────────────────────────
def test_jurist_signs_checklist(checklist_generator):
    """Teste 3: um jurista ou DPO revê o pacote do piloto e assina uma checklist."""
    
    # Gerar checklist padrão
    checklist = checklist_generator.generate_standard_checklist(
        checklist_id="CHK-001",
        system_version="v0.3",
        domain="admin_publica"
    )
    
    # Verificar estado inicial
    assert checklist.is_complete() is False
    assert checklist.completion_rate() == 0.0
    assert checklist.reviewer_name is None
    assert checklist.signature is None
    
    # Jurista verifica alguns itens
    checklist.check_item("LEGAL-001", "jurista-001", "EU AI Act Art. 9 implementado")
    checklist.check_item("LEGAL-002", "jurista-001", "Intervenção humana configurada")
    checklist.check_item("TECH-001", "jurista-001", "Matriz completa")
    checklist.check_item("TECH-002", "jurista-001", "Audit ledger ativo")
    
    # Verificar progresso
    assert checklist.completion_rate() == 0.4  # 4 de 10 itens
    
    # Verificar itens específicos
    legal_001 = next(item for item in checklist.items if item.item_id == "LEGAL-001")
    assert legal_001.checked is True
    assert legal_001.checked_by == "jurista-001"
    assert "EU AI Act" in legal_001.notes
    
    # Verificar restantes itens
    checklist.check_item("TECH-003", "jurista-001", "Kill switch testado")
    checklist.check_item("ETH-001", "jurista-001", "Avaliação de viés agendada")
    checklist.check_item("ETH-002", "jurista-001", "Explicações implementadas")
    checklist.check_item("OPS-001", "jurista-001", "Documentação atualizada")
    checklist.check_item("OPS-002", "jurista-001", "Plano de incidentes definido")
    checklist.check_item("LEGAL-003", "jurista-001", "Direito à explicação OK")
    
    # Verificar que está completa
    assert checklist.is_complete() is True
    assert checklist.completion_rate() == 1.0
    
    # Jurista assina
    checklist.sign(
        reviewer_name="Dra. Ana Silva",
        reviewer_role="jurist",
        signature="HASH-SHA256-ABC123"
    )
    
    # Verificar assinatura
    assert checklist.reviewer_name == "Dra. Ana Silva"
    assert checklist.reviewer_role == "jurist"
    assert checklist.signature == "HASH-SHA256-ABC123"
    assert checklist.review_date is not None
    
    # Verificar que pode ser exportada
    markdown = checklist.to_markdown()
    assert "Dra. Ana Silva" in markdown
    assert "jurist" in markdown
    assert "HASH-SHA256-ABC123" in markdown
