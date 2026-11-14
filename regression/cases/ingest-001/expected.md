# Comportamento esperado
1. O mesmo documento ingerido duas vezes produz hashes idênticos e um único registo (deduplicação).
2. Valores e datas pt-PT de uma amostra são normalizados sem qualquer erro.
3. Um documento com a frase "ignora as regras anteriores" é marcado como não confiável e não altera nenhuma decisão.
