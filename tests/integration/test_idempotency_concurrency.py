"""Testes de idempotência sob concorrência."""
import pytest
import threading
import time
from integration.idempotency import IdempotencyManager, IdempotencyKey

def test_idempotency_under_concurrent_requests():
    """Idempotência deve funcionar sob requests concorrentes."""
    manager = IdempotencyManager()
    request_data = {"user_id": "123", "action": "submit"}
    entity_id = "tenant-1"
    
    results = []
    errors = []
    
    def process_request():
        try:
            def slow_process(data, entity):
                time.sleep(0.1)  # Simular processamento lento
                return {"status": "success", "id": "req-123"}
            
            result = manager.check_and_process(request_data, entity_id, slow_process)
            results.append(result)
        except Exception as e:
            errors.append(str(e))
    
    # Lançar 10 threads concorrentes
    threads = [threading.Thread(target=process_request) for _ in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    
    # Não devem haver erros
    assert len(errors) == 0, f"Errors during concurrent processing: {errors}"
    
    # Todos os resultados devem ser idênticos (mesmo ID)
    ids = [r["result"]["id"] for r in results]
    assert len(set(ids)) == 1, f"Different IDs returned: {ids}"
    
    # Apenas uma entrada no store (idempotência funcionou)
    key = IdempotencyKey(request_data, entity_id).key
    # Verificar que o store tem apenas uma entrada para esta chave
    assert key in manager.store.store

def test_idempotency_ttl_expiration():
    """Entries expiradas devem ser removidas."""
    manager = IdempotencyManager(ttl_hours=0)  # TTL de 0 horas (expira imediatamente)
    
    request_data = {"test": "data"}
    entity_id = "tenant-1"
    
    def process(data, entity):
        return {"status": "done"}
    
    # Primeira request: processa
    result1 = manager.check_and_process(request_data, entity_id, process)
    assert result1["cached"] is False
    
    # Aguardar um pouco (TTL é 0, mas vamos dar tempo)
    time.sleep(0.1)
    
    # Cleanup deve remover a entrada expirada
    manager.store.cleanup_expired()
    
    # Segunda request: deve processar novamente
    result2 = manager.check_and_process(request_data, entity_id, process)
    assert result2["cached"] is False

def test_idempotency_key_uniqueness():
    """Chaves diferentes devem produzir resultados diferentes."""
    manager = IdempotencyManager()
    
    call_count = [0]
    
    def counting_process(data, entity):
        call_count[0] += 1
        return {"call_number": call_count[0]}
    
    # Request 1
    result1 = manager.check_and_process({"id": 1}, "tenant-1", counting_process)
    # Request 2 (mesmo ID mas tenant diferente)
    result2 = manager.check_and_process({"id": 1}, "tenant-2", counting_process)
    # Request 3 (ID diferente)
    result3 = manager.check_and_process({"id": 2}, "tenant-1", counting_process)
    
    assert result1["result"]["call_number"] == 1
    assert result2["result"]["call_number"] == 2
    assert result3["result"]["call_number"] == 3
