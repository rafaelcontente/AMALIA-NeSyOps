# Comportamento esperado
1. A regra gerada coincide com a de referência nos casos de fronteira (fidelidade).
2. Uma regra com erro de sintaxe é devolvida ao LLM no máximo 3 vezes e depois escalada (recuperação de erros).
3. Tentar ativar uma regra gerada sem aprovação humana falha (segurança maker-checker).
