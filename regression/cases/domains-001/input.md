# Caso de Regressão: domains-001

## Módulo
`domains/` — Empacotamento de lógica específica de domínio (piloto: licenciamento comercial)

## Descrição
Validação do sistema de pacotes de domínio que garante:
1. Pack carrega e valida contra contratos do core sem alterar o core
2. Concordância com especialistas no golden set atinge limiar acordado (85%)
3. Casos fora de âmbito escalam em vez de serem decididos

## Pack Piloto
- **ID**: piloto-v0.1
- **Domínio**: Licenciamento comercial
- **Casos**: 20 processos reais anonimizados
- **Regras duras**: R-PIL-001 (maioridade), R-PIL-002 (área mínima), R-PIL-003 (taxa paga)

## Critérios de Aceitação
- Todos os testes passam
- Core imutável durante validação do pack
- Agreement rate >= 85%
- Casos fora de âmbito (área > 500m², risco elevado, tipo industrial) escalam
