# Regras das Aplicações

## 1. Princípio Fundamental
- **Nenhuma lógica de decisão**: Aplicações só consomem API
- **Nunca decidem**: Todas as decisões passam pelo gate via API
- **Sempre registam**: Cada ação gera registo no audit

## 2. ReviewerConsole (Consola do Revisor)
- **Carregamento**: load_case() obtém dados via API
- **Vista completa**: original_text, highlighted_excerpt, evidences, failed_rules, rules_version
- **Ações**: approve, correct, reject, request_info
- **Submissão**: submit_decision() chama API e regista no action_log
- **Fila**: get_queue() retorna casos pendentes

## 3. AuditExplorer (Explorador de Auditoria)
- **Timeline**: get_timeline() retorna linha do tempo completa
- **Integridade**: verify_integrity() verifica cadeia de hashes
- **Pesquisa**: search_events() com filtros
- **Exportação**: JSON ou CSV
- **Só leitura**: Nenhuma modificação de dados

## 4. ManagerDashboard (Painel do Gestor)
- **Métricas**: total_decisions, automatic_decisions, escalated_decisions, human_reviewed
- **Performance**: avg_decision_time_seconds, error_rate
- **Alertas**: drift_alerts, active_alerts
- **Ações**: acknowledge_alert()
- **Exportação**: JSON ou PDF

## 5. RuleEditor (Editor de Regras)
- **Rascunhos**: create_draft() cria rascunho local
- **Testes**: add_test_case(), run_tests()
- **Validação**: validate_expression() via API
- **Submissão**: submit_for_review() envia para revisão
- **Maker-checker**: Jurista cria, revisor aprova

## 6. Acessibilidade WCAG 2.1 AA
8 critérios obrigatórios:
1. **text_alternatives**: Texto alternativo para imagens
2. **keyboard_navigation**: Navegação completa por teclado
3. **sufficient_time**: Sem limites de tempo arbitrários
4. **seizure_safe**: Sem conteúdo intermitente
5. **navigable**: Navegação clara e consistente
6. **readable**: Texto legível e compreensível
7. **predictable**: Comportamento previsível
8. **input_assistance**: Ajuda na entrada de dados

Score = critérios_passados / 8
- **100%**: Todos os critérios passam
- **< 100%**: Interface não acessível

## 7. API Client
- **Todas as operações**: Passam por API client
- **Mock para testes**: MockAPIClient simula respostas
- **Registo automático**: Cada operação gera audit log entry
- **Sem bypass**: Não há métodos que contornam API

## 8. Segurança
- **Zero Trust**: Cada requisição autenticada
- **Autorização**: Verificação de permissões na API
- **Isolamento**: Tenants não acedem a dados de outros
- **Auditoria**: Todas as ações registadas

## 9. Internacionalização
- **Português europeu**: Toda a interface em pt-PT
- **Textos claros**: Linguagem acessível
- **Consistência**: Mesmos termos em toda a aplicação

## 10. Versionamento
- **Regras em uso**: Sempre mostra rules_version
- **Compatibilidade**: API client versionado
- **Depreciação**: Warnings para métodos obsoletos
