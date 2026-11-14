# Resultados esperados

## Teste 1: Maker-checker
- Tentativa de aprovação pelo próprio proposer → ValueError "Maker-checker violado"
- Aprovação por revisor diferente → sucesso
- Decisão gravada com reviewer_id correto

## Teste 2: Metadados da decisão
- Decisão gravada com: reviewer_id, decision, justification, timestamp, trace_id
- Correções opcionais gravadas
- Decisão ligada ao trace (get_decisions_by_trace)
- Justificação com mínimo de 10 caracteres

## Teste 3: Prioridade por risco
- 5 casos com riscos [0.2, 0.9, 0.5, 0.8, 0.3]
- Extração em ordem: [0.9, 0.8, 0.5, 0.3, 0.2]
- Nenhum caso perdido (5 extraídos)
