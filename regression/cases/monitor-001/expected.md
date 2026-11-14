# Resultados esperados

## Teste 1: Deteção de drift
- Baseline: idade ~N(40,10), rendimento ~N(30000,5000)
- Current sem drift: PSI < 0.2, não deteta
- Current COM drift (idade ~N(25,8)): PSI > 0.2, deteta
- Alerta levantado com severidade WARNING
- Alerta registado e recuperável via get_active_alerts()

## Teste 2: Kill switch
- Estado inicial: ativo=False, modo normal
- Após activate(): ativo=True, modo safe
- 100 pedidos processados → 100 em modo safe (escalate)
- 0 pedidos em modo normal
- Após deactivate(): volta ao modo normal

## Teste 3: Shadow mode
- Active: v1.0.0 (score=0.85)
- Shadow: v2.0.0 (score=0.92)
- 20 pedidos processados em shadow mode
- Todas as decisões reais vêm do active (score=0.85)
- Estatísticas: 20 comparações, 0 matches (diferem no score)
- verify_no_real_impact() retorna True
