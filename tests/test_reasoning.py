import pytest
from reasoning.solver import OptimizationSolver
from reasoning.prover import ProofVerifier, Explainer

@pytest.fixture
def solver():
    return OptimizationSolver()

@pytest.fixture
def verifier():
    return ProofVerifier()

@pytest.fixture
def explainer():
    return Explainer()

@pytest.fixture
def candidates():
    return [
        {"id": "A", "cost": 200000, "score": 80, "region": "Lisboa"},
        {"id": "B", "cost": 150000, "score": 70, "region": "Porto"},
        {"id": "C", "cost": 250000, "score": 90, "region": "Lisboa"},
        {"id": "D", "cost": 100000, "score": 60, "region": "Faro"},
    ]

# ─── Teste 1: Verificação independente ──────────────────────────────────────
def test_independent_verification(solver, verifier, candidates):
    """Teste 1: o resultado do solver é confirmado por um verificador independente."""
    budget = 500000
    max_per_region = 2
    
    result = solver.solve_selection_problem(candidates, budget, max_per_region)
    result_dict = result.to_dict()
    
    assert result.feasible is True
    assert verifier.verify_selection(candidates, budget, max_per_region, result_dict) is True
    assert result.objective_value == 220  # A (80) + C (90) + B (70) = 240 (custo 600k? não, orçamento 500k. A+C=450k, score 170. A+B+D=450k, score 210. B+C+D=500k, score 220.)
    # Correção: B(150)+C(250)+D(100) = 500k. Score = 70+90+60 = 220.
    assert result.objective_value == 220

# ─── Teste 2: Instância impossível ──────────────────────────────────────────
def test_infeasible_instance_returns_conflict(solver, candidates):
    """Teste 2: uma instância deliberadamente impossível devolve 'inviável' e o conjunto mínimo de regras em conflito."""
    # Orçamento muito baixo para qualquer combinação válida
    budget = 50000
    max_per_region = 1  # Restrição apertada
    
    result = solver.solve_selection_problem(candidates, budget, max_per_region)
    
    assert result.feasible is False
    assert result.conflict_set is not None
    assert len(result.conflict_set) > 0
    assert "Budget_Constraint" in result.conflict_set

# ─── Teste 3: Prova e explicação ────────────────────────────────────────────
def test_proof_cites_ids_and_explainer_reconstructs(solver, explainer, candidates):
    """Teste 3: a prova devolvida cita ids de regra e de evidência, e explain reconstrói cada passo."""
    budget = 500000
    max_per_region = 2
    
    result = solver.solve_selection_problem(candidates, budget, max_per_region)
    
    # Verificar que a prova contém IDs
    assert len(result.proof) > 0
    has_rule_id = any('rule_id' in step for step in result.proof if step['type'] == 'selection')
    has_evidence_id = any('evidence_id' in step for step in result.proof if step['type'] == 'selection')
    assert has_rule_id
    assert has_evidence_id
    
    # Verificar que o explainer reconstrói a explicação
    explanation = explainer.explain(result.proof)
    assert "Prova de Decisão" in explanation
    assert "Regra" in explanation
    assert "Seleção" in explanation
