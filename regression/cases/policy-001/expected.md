# Comportamento esperado
1. O CI falha se uma regra ativa não tiver pelo menos 1 teste positivo e 1 negativo.
2. As mesmas entradas e a mesma versão do conjunto de regras dão o mesmo veredicto em 100 execuções (determinismo).
3. Uma regra sem aprovação de um segundo revisor (diferente do autor) não consegue passar a "ativa".
