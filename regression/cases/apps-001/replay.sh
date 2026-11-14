#!/bin/bash
# Script para reproduzir o caso de regressão apps-001

set -e

echo "=== Caso de Regressão: apps-001 ==="
echo "Módulo: apps/"
echo "Data: 2026-11-14"
echo ""

# Verificar que o módulo existe
if [ ! -d "apps" ]; then
    echo "❌ Erro: Módulo apps/ não encontrado"
    exit 1
fi

echo "✅ Módulo apps/ encontrado"
echo ""

# Executar testes
echo "Executando testes..."
python -m pytest tests/test_apps.py -v --tb=short

# Verificar warnings
echo ""
echo "Verificando warnings..."
warnings=$(python -m pytest tests/test_apps.py -v 2>&1 | grep -c "DeprecationWarning" || true)

if [ "$warnings" -gt 0 ]; then
    echo "⚠️  Found $warnings deprecation warnings"
    exit 1
else
    echo "✅ Zero warnings de depreciação"
fi

echo ""
echo "=== Caso apps-001 reproduzido com sucesso ==="
