# TODO: Investigação de Casos que Falham

## Casos identificados no golden set v2 (2026-11-14)

### INCOMP-005 (dados_incompletos)
- **Esperado**: rejected
- **Actual**: approved  
- **Descrição**: Falta campo: risco
- **Investigar**: Por que o sistema aprovou um caso com campo obrigatório em falta?
- **Hipóteses**:
  - A verificação de None não está a funcionar correctamente para strings?
  - O campo "risco" não é considerado obrigatório na lógica actual?
  - Bug na order de verificação?

### LLM-ERR-005 (erro_llm)
- **Esperado**: rejected
- **Actual**: approved
- **Descrição**: Documento vazio
- **Investigar**: Por que documento vazio não é rejeitado?
- **Hipóteses**:
  - Falta validação de documento não-vazio?
  - String vazia passa pela verificação de tipo?

## Prioridade
- Investigar após conformal prediction estar implementado
- Pode requerer ajustes na decision_fn do golden set v2
- Documentar findings e adicionar testes de regressão
