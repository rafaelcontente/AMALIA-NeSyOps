# Regras de Integração

## 1. Idempotência
- **Chave única**: Hash SHA256 do request + entity_id
- **TTL**: 24 horas por defeito (configurável)
- **Cache**: Resultados armazenados com timestamp de expiração
- **Cleanup**: Remoção automática de entradas expiradas
- **Garantia**: Mesmo request nunca é processado duas vezes

## 2. Isolamento Multi-Tenant
- **Entity ID**: Cada tenant tem ID único e imutável
- **Verificação**: Todas as operações verificam entity_id do requester
- **PermissionError**: Lançado quando acesso não autorizado
- **Dados**: Armazenados em dicionário separado por entity_id
- **Listagem**: Apenas retorna dados do próprio tenant

## 3. Gate Enforcement
- **Pilar 6**: Nenhuma ação crítica existe fora do gate
- **API Gateway**: Todas as submissões passam por gate.evaluate()
- **Autorização**: Verificação de user_id → entity_id antes de qualquer operação
- **Bypass**: Não há métodos direct_decision ou bypass_gate
- **Transparência**: Todos os resultados incluem verdict do gate

## 4. Autenticação e Autorização
- **TenantManager**: Regista tenants e utilizadores
- **TenantContext**: Contém entity_id, user_id, permissions
- **verify_access()**: Verifica se user pertence ao tenant
- **Permissões**: Lista de permissões por utilizador (read, write, admin)

## 5. Processamento Assíncrono
- **Submissão**: Retorna trace_id imediatamente (HTTP 202)
- **Polling**: GET /decisions/{trace_id} para obter resultado
- **Webhooks**: Notificação assíncrona quando decisão completa
- **Status**: processing → completed → resultado disponível

## 6. Ferramentas Externas (MCP)
- **MCPServer**: Expõe ferramentas para agentes
- **Registo**: Ferramentas registadas com nome, descrição, parâmetros
- **Chamadas**: Histórico de chamadas armazenado
- **Isolamento**: Chamadas associadas a entity_id

## 7. Adaptadores
- **ExternalSystemAdapter**: Base para todos os adaptadores
- **OpenDataAdapter**: Dados abertos (dados.gov.pt)
- **LegacySystemAdapter**: Sistemas legados
- **EntityResolutionAdapter**: Resolução de entidades e screening
- **Histórico**: Todas as chamadas registadas

## 8. Zero Trust Architecture
- **Verificação sempre**: Nenhuma operação assume autorização prévia
- **Isolamento completo**: Tenants não partilham dados
- **Gate obrigatório**: Todas as decisões passam pelo gate
- **Auditoria**: Todas as operações registadas
