#!/bin/bash
# Script para reproduzir o caso de regressão domains-001

set -e

echo "=== Caso de Regressão: domains-001 ==="
echo "Módulo: domains/"
echo "Data: 2026-11-14"
echo ""

# Verificar que o módulo existe
if [ ! -d "domains" ]; then
    echo "❌ Erro: Módulo domains/ não encontrado"
    exit 1
fi

echo "✅ Módulo domains/ encontrado"
echo ""

# Executar testes
echo "Executando testes..."
python -m pytest tests/test_domains.py -v --tb=short

echo ""
echo "=== Caso domains-001 reproduzido com sucesso ==="
