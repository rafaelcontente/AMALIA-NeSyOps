# Resultados esperados

## Teste 1: Matriz de rastreabilidade
- 3 regras: R-012 (completa), R-020 (completa), R-031 (sem teste)
- R-012: source_norm="Lei n.º 123/2024", test_id="T-044", status="complete"
- R-020: source_norm="Decreto-Lei n.º 456/2023", test_id="T-045", status="complete"
- R-031: test_id="SEM_TESTE", status="missing_test"
- Estatísticas: total=3, complete=2, missing_tests=1
- get_missing_tests() retorna [R-031]

## Teste 2: Reprodutibilidade do pacote
- Model card gerado duas vezes com mesmos metadados
- Campos principais idênticos (name, version, description, metrics)
- Markdown exportável com "# Model Card: AMALIA v0.3"
- Mapeamento EU AI Act: coverage_rate > 0
- EU-AI-001 mapeado para R-012

## Teste 3: Checklist assinada por jurista
- Checklist gerada com 10 itens
- Estado inicial: complete=False, completion_rate=0.0
- Após verificar 4 itens: completion_rate=0.4
- Após verificar todos: complete=True, completion_rate=1.0
- Assinatura: reviewer_name="Dra. Ana Silva", role="jurist"
- Markdown exportável com nome, função e assinatura
