# Regras aplicadas

## Regra R-001 (Maioridade)
- Descrição: Utilizador deve ter 18 ou mais anos
- Expressão: idade >= 18
- Severity: HARD
- Status: ACTIVE
- Test cases:
  - idade=20 → True
  - idade=17 → False

## Fluxo maker-checker
- Regras devem passar por: DRAFT → REVIEWED → APPROVED → ACTIVE
- Não podem saltar estados
- Necessitam de revisor aprovado

## Validação em 5 camadas
1. Structure (estrutura básica)
2. Consistency (consistência de dados)
3. Domain Rules (regras de domínio via policy/)
4. Plausibility (plausibilidade/confiança)
5. Claims (verificação de evidências)
