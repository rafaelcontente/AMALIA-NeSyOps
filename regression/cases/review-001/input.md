# Teste do módulo review/

## Descrição
Interface humana para casos escalados com prioridade por risco, maker-checker e auditoria pós-hoc.

## Requisitos testados
1. O utilizador que gerou a proposta não consegue aprovar o próprio caso (maker-checker)
2. Toda a decisão humana grava revisor, hora e justificação, e liga ao trace
3. Com a fila cheia, os casos de maior risco são servidos primeiro e nenhum se perde
