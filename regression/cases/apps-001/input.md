# Caso de Regressão: apps-001

## Módulo
`apps/` — Interfaces para revisor, auditor, jurista e gestor (sem lógica de decisão)

## Descrição
Validação das aplicações finais que garantem:
1. Revisor conclui caso apenas com informação do ecrã
2. App não consegue alterar decisão sem passar pela API
3. Cumpre critérios de acessibilidade WCAG 2.1 AA

## Aplicações Implementadas
- **ReviewerConsole**: Consola do revisor (fila, evidências, regras falhadas)
- **AuditExplorer**: Explorador de auditoria (linha do tempo, verificação de integridade)
- **ManagerDashboard**: Painel do gestor (métricas do monitor)
- **RuleEditor**: Editor de regras para juristas (texto ↔ regra ↔ testes)
- **AccessibilityChecker**: Verificação de acessibilidade web

## Critérios de Aceitação
- Todos os testes passam
- Zero warnings de depreciação
- Aplicações só consomem API, nunca decidem
- Acessibilidade WCAG 2.1 AA verificada
