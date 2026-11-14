# Resultado Esperado

## Teste 1: Pack carrega sem alterar core
- Pack carregado com sucesso (pack_id="piloto", version="v0.1")
- Validação contra core retorna valid=True
- Zero violations
- Core contracts não são modificados (version, required_fields, immutable mantidos)
- Pack contém todos os componentes (ontology, policy, sources, golden_set, templates, limits)

## Teste 2: Concordância com especialistas
- 20 casos processados
- >= 17 decisões automáticas
- 0 violações de regras duras
- Agreement rate >= 85%
- meets_threshold = True

## Teste 3: Casos fora de âmbito escalam
- Limites documentados (in_scope, out_of_scope, escalation_criteria)
- Caso dentro do âmbito: is_in_scope = True
- Caso com área 600m² (> 500): is_in_scope = False
- Caso com risco elevado: is_in_scope = False
- Caso com tipo industrial: is_in_scope = False

## Critérios de escalonamento
- "área_m2 > 500"
- "risco == 'elevado'"
- "tipo == 'industrial'"
