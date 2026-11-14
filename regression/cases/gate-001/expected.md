# Resultados esperados

## Teste 1: Bloqueio de propostas defeituosas
- 5 propostas com defeitos conhecidos devem ser bloqueadas
- Conteúdo vazio → REJECTED
- Datas inconsistentes → REJECTED
- Idade < 18 → REJECTED (viola regra R-001)
- Confiança baixa → REJECTED
- Afirmação sem evidência → REJECTED

## Teste 2: Taxa de falsos positivos
- 100 propostas corretas
- Taxa de falsos positivos ≤ 5% (no máximo 5 rejeitadas)

## Teste 3: Falha do validador
- Validador que lança exceção
- Proposta deve ser REJECTED com mensagem "Validador falhou"
