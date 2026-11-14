# Operations Manual (AMALIA-NeSyOps)

## 1. Deployment
- **Python**: 3.11, 3.12, ou 3.13.
- **Env Vars**: `OLLAMA_HOST`, `OLLAMA_MODEL`, `JWT_SECRET`, `AUDIT_DB_PATH`.
- **Start**: `uvicorn integration.api:app --host 0.0.0.0 --port 8000 --workers 4`

## 2. Upgrade & Rollback
1. Backup: `cp /var/lib/amalia/audit.db /var/lib/amalia/audit.db.bak`
2. Update: `git pull && pip install -r requirements.txt`
3. Verify: `python -m pytest tests/ -q`
4. Rollback: Restaurar DB e `git checkout <commit-anterior>`.

## 3. Known Limits
- Max Payload: 50 MB
- Rate Limit: 100 req/min por `entity_id`
- LLM Timeout: 30s (Circuit breaker abre após 3 falhas)
- DB Size: ~100MB por 100k decisões (SQLite WAL)

## 4. Runbooks
- **Circuit Breaker Open**: Verificar Ollama (`curl http://localhost:11434/api/tags`). Reiniciar se necessário.
- **Audit Chain Broken**: Não modificar a DB. Executar `IntegrityChecker`. Notificar DPO se houver suspeita de manipulação.
- **OOM**: Reduzir workers do Uvicorn. Garantir que a `review/queue.py` está a ser processada.

## 5. Monitoring
Alertar em: erros `5xx` > 1%, latência p95 > 2.0s, `circuit_breaker_state="open"`, ou `audit_chain_valid=0`.
