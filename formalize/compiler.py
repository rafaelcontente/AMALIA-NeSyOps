import ast
from policy.engine import SafeExpressionEvaluator

class RuleCompiler:
    def __init__(self):
        self.evaluator = SafeExpressionEvaluator()

    def compile(self, expression: str) -> bool:
        try:
            tree = ast.parse(expression, mode='eval')
            for node in ast.walk(tree):
                if type(node) not in self.evaluator.ALLOWED_NODES:
                    raise ValueError(f"Nó não permitido: {type(node).__name__}")
            return True
        except SyntaxError as e:
            raise ValueError(f"Erro de sintaxe: {e}")
        except ValueError as e:
            raise ValueError(f"Erro de segurança/semântica: {e}")
