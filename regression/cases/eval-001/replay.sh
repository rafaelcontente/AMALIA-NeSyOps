#!/bin/bash
# Script para reproduzir o caso de regressão eval-001

set -e

echo "=== Caso de Regressão: eval-001 ==="
echo "Módulo: eval/"
echo "Data: 2026-11-14"
echo ""

# Verificar que o módulo existe
if [ ! -d "eval" ]; then
    echo "❌ Erro: Módulo eval/ não encontrado"
    exit 1
fi

echo "✅ Módulo eval/ encontrado"
echo ""

# Executar testes
echo "Executando testes..."
python -m pytest tests/test_eval.py -v --tb=short

# Verificar warnings
echo ""
echo "Verificando warnings..."
warnings=$(python -m pytest tests/test_eval.py -v 2>&1 | grep -c "DeprecationWarning" || true)

if [ "$warnings" -gt 0 ]; then
    echo "⚠️  Found $warnings deprecation warnings"
    exit 1
else
    echo "✅ Zero warnings de depreciação"
fi

echo ""
echo "=== Caso eval-001 reproduzido com sucesso ==="
