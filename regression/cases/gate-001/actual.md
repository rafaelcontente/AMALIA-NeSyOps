# Resultados observados

## Teste 1: Bloqueio de propostas defeituosas
✅ Todas as 5 propostas defeituosas foram bloqueadas
✅ Conteúdo vazio → REJECTED
✅ Datas inconsistentes → REJECTED
✅ Idade < 18 → REJECTED
✅ Confiança baixa → REJECTED
✅ Afirmação sem evidência → REJECTED

## Teste 2: Taxa de falsos positivos
✅ 0 falsos positivos em 100 propostas corretas
✅ Taxa de falsos positivos: 0% (muito abaixo do limite de 5%)

## Teste 3: Falha do validador
✅ Proposta REJECTED quando validador lança exceção
✅ Mensagem de erro registada corretamente

## Fluxo maker-checker
✅ Regra R-001 criada e aprovada corretamente (DRAFT → REVIEWED → APPROVED → ACTIVE)
