# Regras aplicadas

## Deteção de drift
- PSI (Population Stability Index) para dados tabulares
- Threshold PSI > 0.2 = drift significativo
- Similaridade cosseno para embeddings
- Threshold 1 - cosine_similarity > 0.1 = drift significativo
- Baseline definido via set_baseline()

## Kill switch
- Estados: active (bool), safe_mode (ESCALATE | REJECT)
- activate(reason, activated_by, mode) → ativa interruptor
- deactivate(deactivated_by, reason) → desativa interruptor
- process_request() → retorna modo safe se ativo
- Histórico de ativações/desativações mantido

## Shadow mode
- active_version: versão em produção (decisões reais)
- shadow_version: versão candidata (apenas comparação)
- run_shadow() executa ambos em paralelo
- Apenas resultado do active é devolvido (real)
- Resultado do shadow é apenas registado (observabilidade)
- verify_no_real_impact() verifica que shadow não afetou decisões

## Sistema de alertas
- Severidade: INFO | WARNING | CRITICAL
- Cooldown: 60 minutos por defeito (evita spam)
- raise_alert() respeita cooldown (exceto se force=True)
- get_active_alerts() retorna alertas não reconhecidos
- acknowledge(alert_id) marca alerta como reconhecido
