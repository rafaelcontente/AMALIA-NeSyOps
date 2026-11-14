# Comportamento esperado
1. Todos os modelos são frozen=True (imutáveis).
2. Proposal com campo obrigatório em falta rejeitada com erro nomeando o campo.
3. Decision sem trace_id ou versões (model/prompt/rules) não pode ser construída.
4. Serialização/desserialização preserva igualdade e hash em 100% dos casos.
