"""Domínio piloto: licenciamento comercial."""
from .pack import (
    DomainPack, DomainOntology, DomainPolicy, DomainSources,
    DomainGoldenSet, DomainTemplates, DomainLimits
)

def create_piloto_pack() -> DomainPack:
    """Cria pacote de domínio piloto para licenciamento comercial."""
    
    # Ontologia do domínio
    ontology = DomainOntology(
        entities=[
            "requerente",
            "estabelecimento",
            "licença",
            "actividade_económica"
        ],
        relationships=[
            {"from": "requerente", "to": "estabelecimento", "type": "possui"},
            {"from": "estabelecimento", "to": "licença", "type": "requer"},
            {"from": "licença", "to": "actividade_económica", "type": "autoriza"}
        ],
        attributes={
            "requerente": ["nif", "nome", "morada", "idade"],
            "estabelecimento": ["área_m2", "localização", "tipo"],
            "licença": ["tipo", "duração", "taxa"],
            "actividade_económica": ["código_cae", "descrição", "risco"]
        }
    )
    
    # Regras do domínio
    policy = DomainPolicy(
        rules=[
            {
                "id": "R-PIL-001",
                "name": "Maioridade do requerente",
                "expression": "idade >= 18",
                "severity": "hard"
            },
            {
                "id": "R-PIL-002",
                "name": "Área mínima do estabelecimento",
                "expression": "área_m2 >= 20",
                "severity": "hard"
            },
            {
                "id": "R-PIL-003",
                "name": "Taxa paga",
                "expression": "taxa_paga == True",
                "severity": "hard"
            },
            {
                "id": "R-PIL-004",
                "name": "Actividade de baixo risco",
                "expression": "risco in ['baixo', 'médio']",
                "severity": "soft"
            }
        ],
        hard_rules=["R-PIL-001", "R-PIL-002", "R-PIL-003"],
        soft_rules=["R-PIL-004"]
    )
    
    # Fontes legais
    sources = DomainSources(
        legal_sources=[
            {
                "id": "DL-10-2015",
                "name": "Decreto-Lei n.º 10/2015",
                "description": "Regime jurídico de acesso e exercício de actividades de comércio"
            },
            {
                "id": "Portaria-123-2016",
                "name": "Portaria n.º 123/2016",
                "description": "Taxas de licenciamento comercial"
            }
        ],
        normative_texts=[
            {
                "id": "NT-001",
                "text": "O requerente deve ter pelo menos 18 anos de idade.",
                "source": "DL-10-2015, art. 5.º"
            },
            {
                "id": "NT-002",
                "text": "O estabelecimento deve ter área mínima de 20 m².",
                "source": "DL-10-2015, art. 12.º"
            }
        ],
        precedents=[
            {
                "id": "PREC-001",
                "case": "Licenciamento de café com 15 m²",
                "decision": "rejected",
                "reason": "Área inferior ao mínimo legal"
            }
        ]
    )
    
    # Golden set (20 casos reais anonimizados)
    golden_set = DomainGoldenSet(
        cases=[
            {
                "id": f"CASE-{i:03d}",
                "requerente": {"idade": 25 + (i % 30), "nif": f"500{i:06d}"},
                "estabelecimento": {"área_m2": 20 + (i % 50), "tipo": "comércio"},
                "licença": {"tipo": "comércio", "taxa_paga": True},
                "actividade_económica": {"risco": "baixo" if i % 2 == 0 else "médio"}
            }
            for i in range(1, 21)
        ],
        expert_decisions={
            f"CASE-{i:03d}": {
                "decision": "approved" if (25 + (i % 30) >= 18 and 20 + (i % 50) >= 20) else "rejected",
                "confidence": 0.95,
                "expert_id": "expert-001"
            }
            for i in range(1, 21)
        },
        agreement_threshold=0.85
    )
    
    # Templates de explicação
    templates = DomainTemplates(
        approval_template="""
A sua licença comercial foi **aprovada**.

**Motivo:** O estabelecimento cumpre todos os requisitos legais:
- Requerente maior de idade ({idade} anos)
- Área do estabelecimento adequada ({área_m2} m²)
- Taxa de licenciamento paga

**Fundamentação legal:** Decreto-Lei n.º 10/2015, artigos 5.º e 12.º

**Próximos passos:** A licença será emitida no prazo de 5 dias úteis.
""",
        rejection_template="""
A sua licença comercial foi **rejeitada**.

**Motivo:** O estabelecimento não cumpre os seguintes requisitos:
{violations}

**Fundamentação legal:** Decreto-Lei n.º 10/2015

**Direito de recurso:** Pode recorrer desta decisão no prazo de 15 dias úteis.
""",
        escalation_template="""
O seu caso requer **análise manual** por um técnico especializado.

**Motivo:** {reason}

**Próximos passos:** Um técnico contactá-lo-á no prazo de 10 dias úteis.
"""
    )
    
    # Limites do domínio
    limits = DomainLimits(
        in_scope=[
            "Licenciamento de estabelecimentos comerciais",
            "Actividades de comércio a retalho",
            "Estabelecimentos com área entre 20 e 500 m²"
        ],
        out_of_scope=[
            "Licenciamento industrial",
            "Actividades de restauração e bebidas",
            "Estabelecimentos com área superior a 500 m²",
            "Actividades de risco elevado"
        ],
        escalation_criteria=[
            "área_m2 > 500",
            "risco == 'elevado'",
            "tipo == 'industrial'"
        ],
        binary_decisions=True,
        ordinal_decisions=False
    )
    
    # Criar pack completo
    pack = DomainPack(
        pack_id="piloto",
        version="v0.1",
        name="Licenciamento Comercial (Piloto)",
        description="Domínio piloto para licenciamento de estabelecimentos comerciais",
        ontology=ontology,
        policy=policy,
        sources=sources,
        golden_set=golden_set,
        templates=templates,
        limits=limits
    )
    
    return pack
