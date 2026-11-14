# Regras aplicadas

## Maker-checker
- Quem gerou a proposta (proposer_id) não pode aprovar o próprio caso
- Revisor deve ser diferente do proposer
- Validação em tempo de decisão

## Metadados obrigatórios
- reviewer_id: identificador do revisor humano
- decision: approved | rejected | corrected | request_info
- justification: texto com mínimo de 10 caracteres
- timestamp: hora UTC da decisão
- trace_id: ligação ao trace original

## Prioridade da fila
- priority_score = risk_factor * 0.5 + confidence_factor * 0.3 + deadline_factor * 0.2
- risk_factor = 1.0 - risk_score (risco alto = prioridade alta)
- confidence_factor = confidence (confiança baixa = prioridade alta)
- deadline_factor = horas_restantes / 24 (prazo curto = prioridade alta)

## Status do caso
- pending: aguarda decisão
- approved: aprovado
- rejected: rejeitado
- corrected: aprovado com correção
