"""Meta-teste: Valida a integridade do mapeamento de conformidade."""
import json
import pathlib
import pytest

@pytest.fixture
def mapping_data():
    with open("compliance/eu_ai_act_mapping.json", "r", encoding="utf-8") as f:
        return json.load(f)

def test_mapping_file_exists_and_is_valid(mapping_data):
    """O ficheiro de mapeamento deve existir e ser JSON válido."""
    assert "framework" in mapping_data
    assert mapping_data["framework"] == "EU AI Act"
    assert "mappings" in mapping_data
    assert len(mapping_data["mappings"]) >= 5

def test_all_referenced_tests_exist(mapping_data):
    """Todos os testes referenciados no mapeamento devem existir no repositório."""
    root = pathlib.Path(__file__).resolve().parents[2]
    
    for mapping in mapping_data["mappings"]:
        for test_path in mapping["evidence_tests"]:
            file_path_str = test_path.split("::")[0]
            file_path = root / file_path_str
            
            assert file_path.exists(), f"Teste referenciado não existe: {file_path}"
            
            test_func = test_path.split("::")[1] if "::" in test_path else None
            if test_func:
                content = file_path.read_text(encoding="utf-8")
                assert f"def {test_func}" in content, f"Função de teste não encontrada em {file_path}: {test_func}"

def test_all_mappings_have_required_fields(mapping_data):
    """Cada mapeamento deve ter os campos obrigatórios."""
    required_fields = ["article", "requirement", "description", "evidence_tests", "status"]
    for mapping in mapping_data["mappings"]:
        for field in required_fields:
            assert field in mapping, f"Campo '{field}' em falta no mapeamento {mapping.get('article', 'UNKNOWN')}"
        assert mapping["status"] in ["covered", "partially_covered", "evidence_ready", "gap"], f"Status inválido: {mapping['status']}"
