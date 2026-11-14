# Caso de Regressão: eval-001

## Módulo
`eval/` — Avaliação contínua, golden sets, red teaming e baseline comparison

## Descrição
Validação do sistema de avaliação contínua que garante:
1. CI falha automaticamente perante regressões acima do limiar
2. Ataques de injeção de prompt não alteram decisões
3. Baseline sem LLM é medido e sistema completo supera-o

## Testes Implementados
- `test_ci_fails_on_regression`: Verifica que regressão de 96% → 93% falha CI
- `test_prompt_injection_does_not_alter_decisions`: Verifica robustez contra 5 ataques de injeção
- `test_baseline_measured_and_system_surpasses`: Verifica medição de baseline e comparação

## Critérios de Aceitação
- Todos os testes passam
- Relatório de avaliação gera status correto (pass/fail/warning)
- Zero warnings de depreciação
