# Resultados observados

## Teste 1: Tampering detection
✅ 3 entradas adicionadas com sucesso
✅ Cadeia verificada como íntegra (valid=True)
✅ Entrada 2 adulterada manualmente (idade: 999)
✅ Verificação deteta quebra em broken_at=1
✅ Mensagem: "Hash inválido no registo 1"

## Teste 2: Replay determinístico
✅ Golden set: 5 casos de teste
✅ Replay reproduz veredictos para todas as idades
✅ Idades 25, 30, 18 → passed=True (idade >= 18)
✅ Idades 17, 16 → passed=False (idade < 18)
✅ match=True para 5/5 casos (100% de reprodução)

## Teste 3: Right to erasure (RGPD)
✅ Entrada com dados pessoais adicionada
✅ Cadeia íntegra antes do apagamento
✅ right_to_erasure aplicado ao trace T-9f2a1b3c
✅ Dados pessoais removidos (input_data = {"_redacted": True})
✅ Pseudónimo mantido (input_pseudonym presente)
✅ Hashes recalculados após apagamento
✅ Cadeia continua íntegra após apagamento (valid=True)

## Integridade da cadeia
✅ Hash chain implementada corretamente
✅ Cada entrada inclui hash da anterior
✅ Tampering detetado imediatamente
✅ Apagamento preserva integridade da cadeia
