# Regras de Domínio

## 1. Estrutura do Pack
- Cada pack tem: ontology, policy, sources, golden_set, templates, limits
- Versionamento independente do core
- Validação contra contratos do core sem alterar o core
- Documentação explícita do que o pack NÃO decide

## 2. Critérios para Piloto
- Texto normativo delimitado
- Decisões binárias ou ordenáveis
- Dados acessíveis
- Especialistas disponíveis
- Âmbito claramente definido

## 3. Golden Set
- >= 20 casos reais anonimizados
- Decisões anotadas por especialistas
- Threshold de concordância >= 85%
- Cobertura de casos dentro e fora do âmbito

## 4. Escalonamento Automático
Casos fora de âmbito escalam para revisão humana:
- Área superior a 500 m²
- Risco elevado
- Tipo industrial
- Qualquer critério definido em escalation_criteria

## 5. Busca Aninhada
Campos podem estar em sub-entidades:
- `idade` → `requerente.idade`
- `área_m2` → `estabelecimento.área_m2`
- `risco` → `actividade_económica.risco`

A função `_get_nested_value` busca em múltiplos níveis:
1. Acesso directo
2. Caminho com ponto
3. Busca profunda em sub-entidades

## 6. Regras Duras vs Suaves
- **Hard rules**: violação = rejeição automática (R-PIL-001, R-PIL-002, R-PIL-003)
- **Soft rules**: violação = warning ou escalonamento (R-PIL-004)
- Zero violações de regras duras no golden set

## 7. Templates de Explicação
- **Aprovação**: motivo + fundamentação legal + próximos passos
- **Rejeição**: motivo + violações + direito de recurso
- **Escalonamento**: motivo + prazo de contacto

## 8. Validação contra Core
- Pack valida contra core_contracts
- Core permanece imutável
- Violações bloqueiam carregamento
- Warnings são informativos
