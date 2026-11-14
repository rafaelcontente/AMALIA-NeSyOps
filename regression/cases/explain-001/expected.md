# Resultados esperados

## Teste 1: Zero afirmações órfãs
- Vista do cidadão: todas as referências existem no trace
- Vista do auditor: todas as referências existem no trace
- Validação: {"valid": true, "orphan_claims": []}

## Teste 2: Trace diferente → explicação diferente
- Decisão aprovada vs indeferida produzem textos diferentes
- Decisão aprovada contém "aprovada"
- Decisão indeferida contém "indeferida" e "recurso"

## Teste 3: Compreensão
- Comprimento médio das frases < 25 palavras
- Presença de palavras-chave: "motivo", "referências"
- Para decisões indeferidas: presença de "recurso" e "prazo"
- Explicação tem conteúdo substancial (> 100 caracteres)
