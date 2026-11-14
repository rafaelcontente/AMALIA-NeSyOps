# Teste do módulo monitor/

## Descrição
Deteção de drift, kill switch, shadow mode e sistema de alertas.

## Requisitos testados
1. Um drift injetado num dataset de teste dispara alerta dentro do prazo definido
2. Com o kill switch ativo, 100% dos novos pedidos vão para modo seguro e não sai nenhuma decisão automática
3. Uma nova versão em shadow mode gera comparação com a versão ativa sem afetar nenhuma decisão real
