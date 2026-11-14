# Resultados observados

## Teste 1: Deteção de drift
✅ Baseline definido: idade ~N(40,10), rendimento ~N(30000,5000)
✅ Current sem drift: PSI < 0.2, drift_detected=False
✅ Current COM drift (idade ~N(25,8)): PSI > 0.2, drift_detected=True
✅ Alerta levantado: severity=WARNING, message contém "idade"
✅ Alerta registado em active_alerts

## Teste 2: Kill switch
✅ Estado inicial: active=False, mode=normal
✅ activate() chamado com reason="Salto anómalo na taxa de violações de R-012"
✅ active=True, safe_mode=ESCALATE
✅ 100 pedidos processados: 100 safe, 0 normal
✅ Todos os pedidos safe têm action="escalate" e reason correto
✅ deactivate() chamado: active=False
✅ Pedido após deactivate: mode=normal

## Teste 3: Shadow mode
✅ set_shadow("v2.0.0") configurado
✅ 20 pedidos processados em shadow mode
✅ Todas as 20 decisões reais: version="v1.0.0", score=0.85
✅ Shadow comparado: version="v2.0.0", score=0.92
✅ Estatísticas: total=20, matches=0, mismatches=20, match_rate=0.0
✅ verify_no_real_impact() retorna True

## Métricas de drift
✅ PSI (Population Stability Index) calculado corretamente
✅ Threshold 0.2 aplicado
✅ Similaridade cosseno para embeddings (threshold 0.1)

## Sistema de alertas
✅ AlertManager com cooldown de 60 minutos
✅ Alerta levantado com force=True (ignora cooldown)
✅ Alerta recuperável via get_active_alerts()
