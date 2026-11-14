# Resultados esperados

## Teste 1: Tampering detection
- Adicionar 3 entradas válidas → cadeia íntegra
- Alterar manualmente entrada 2 → cadeia quebrada
- Verificação identifica broken_at=1 com mensagem "Hash inválido"

## Teste 2: Replay determinístico
- Golden set com 5 decisões (idades: 25, 30, 17, 18, 16)
- Replay reproduz 100% dos veredictos originais
- match=True para todas as entradas

## Teste 3: Right to erasure (RGPD)
- Entrada com dados pessoais (nome: "João Silva")
- Aplicar right_to_erasure → dados removidos, pseudónimo mantido
- Recalcular hashes → cadeia continua íntegra
- Verificação após apagamento: valid=True
