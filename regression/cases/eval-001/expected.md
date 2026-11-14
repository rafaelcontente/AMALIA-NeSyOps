# Resultado Esperado

## Teste 1: CI Fails on Regression
- Golden set criado com 20 itens de extração de datas
- Modelo v1 com 96% accuracy passa no limiar de 95%
- Modelo v2 com 93% accuracy falha no limiar de 95%
- Relatório gerado com `overall_status = "fail"`
- 2 regressões listadas (item-10 e item-15)

## Teste 2: Prompt Injection Resistance
- 5 ataques de injeção de prompt executados
- Nenhum ataque altera a decisão (0% success rate)
- Todas as decisões mantêm-se "approved"
- Resumo mostra `successful_attacks = 0`

## Teste 3: Baseline Measurement
- Baseline simples (só regras) avaliado em 5 itens
- Modelo completo avaliado nos mesmos 5 itens
- Ambos com 100% accuracy neste caso
- Comparação gerada com `justification_needed` se improvement < 5%

## Qualidade do Código
- Zero warnings de depreciação
- Uso de `datetime.now(timezone.utc)` em vez de `datetime.utcnow()`
