# Resultados observados

## Teste 1: Maker-checker
✅ Tentativa de aprovação pelo proposer (agent-001) → ValueError
✅ Aprovação por reviewer-001 → sucesso
✅ Decisão gravada com reviewer_id="reviewer-001"

## Teste 2: Metadados da decisão
✅ reviewer_id="jurista-001" gravado
✅ decision="corrected" gravado
✅ justification com "45 dias" presente
✅ corrections={"prazo": 45} gravado
✅ timestamp não-nulo
✅ trace_id="T-002" ligado à decisão
✅ get_decisions_by_trace retorna 1 decisão

## Teste 3: Prioridade por risco
✅ 5 casos adicionados à fila
✅ Extração em ordem: [0.9, 0.8, 0.5, 0.3, 0.2]
✅ 5/5 casos extraídos (nenhum perdido)

## Fila de prioridade
✅ Heap min-heap com priority_score combinado
✅ Risco alto = prioridade alta
✅ Confiança baixa = prioridade alta
✅ Prazo curto = prioridade alta
