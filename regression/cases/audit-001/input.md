# Teste do módulo audit/

## Descrição
Registo imutável de auditoria com hash chain, replay determinístico e gestão de privacidade (RGPD).

## Requisitos testados
1. Alterar manualmente um registo quebra a verificação da cadeia e identifica o ponto da quebra
2. Com as mesmas versões e dados, o replay reproduz o veredicto de 100% das decisões do golden set
3. Um pedido de apagamento ou uma retenção expirada remove os dados pessoais sem invalidar a verificação da cadeia
