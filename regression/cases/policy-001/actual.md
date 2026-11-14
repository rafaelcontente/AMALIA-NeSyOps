# Comportamento observado
✅ Teste 1 (cobertura de testes): PASSED — ativação bloqueada sem testes positivo/negativo.
✅ Teste 2 (determinismo): PASSED — 100 execuções idênticas.
✅ Teste 3 (maker-checker): PASSED — transições de estado bloqueadas sem revisão independente.
✅ Teste 4 (segurança AST): PASSED — injeção de código maliciosa (__import__('os').system('rm -rf /')) bloqueada com SecurityError.
✅ Refatoração concluída: eval() inseguro substituído por SafeExpressionEvaluator baseado em AST.
