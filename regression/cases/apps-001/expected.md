# Resultado Esperado

## Teste 1: Revisor conclui caso com informação do ecrã
- Case view carregada com: trace_id, original_text, highlighted_excerpt, evidences, failed_rules, rules_version
- 4 ações disponíveis: approve, correct, reject, request_info
- Decisão submetida via API com sucesso
- Ação registada no action_log

## Teste 2: App não altera decisão sem API
- submit_decision() chama API e gera registo
- API regista decisão no audit_log
- Não há métodos de bypass (direct_decision, bypass_api)
- Todas as ações passam pela API

## Teste 3: Acessibilidade WCAG 2.1 AA
- 8 critérios verificados: text_alternatives, keyboard_navigation, sufficient_time, seizure_safe, navigable, readable, predictable, input_assistance
- Interface acessível: passed=True, score=1.0
- Interface inacessível: passed=False, score<1.0, falhas detectadas
- Relatório gerado em formato legível

## Qualidade do Código
- Zero warnings
- datetime.now(timezone.utc) usado
- Type hints completos com Pydantic
