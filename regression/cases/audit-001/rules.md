# Regras aplicadas

## Regra R-001 (Maioridade)
- Expressão: idade >= 18
- Severity: HARD
- Usada no golden set para teste de replay

## Hash Chain
- Cada entrada contém previous_hash (hash da entrada anterior)
- entry_hash = SHA256(todos os campos da entrada)
- Primeira entrada tem previous_hash=None

## Pseudonimização (RGPD)
- Campos sensíveis: nome, email, nif, morada, telefone
- Pseudónimo = SHA256(dados sensíveis + salt)
- Dados originais podem ser removidos sem quebrar cadeia

## Replay determinístico
- Usa versões de modelo, prompt e regras do entry
- Avalia regras com RuleEvaluator
- Compara veredicto original vs reproduzido
- match=True se rules_evaluated, rules_violated e passed forem iguais

## Right to erasure (Artigo 17 RGPD)
- Remove dados pessoais, mantém pseudónimo
- Recalcula hashes para preservar cadeia
- Marca input_data como {"_redacted": True}
