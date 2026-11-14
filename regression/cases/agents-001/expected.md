# Comportamento esperado
1. Em 100 execuções do mesmo pedido, pelo menos 95% das saídas passam a validação de schema.
2. Um agente em loop é interrompido ao atingir o limite de passos e o caso é escalado.
3. A chamada a uma ferramenta fora da lista de permissões é bloqueada e registada.
