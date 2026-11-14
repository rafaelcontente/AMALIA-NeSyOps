"""
Motor de avaliação de regras seguro (AST-based).
Substitui o eval() inseguro por um parser que apenas permite operações lógicas e de comparação básicas.
"""
import ast
from typing import Any
from policy.models import Rule, RuleSet, RuleStatus, RuleSeverity


class SecurityError(Exception):
    """Exceção levantada quando uma expressão viola as regras de segurança do AST."""
    pass


class SafeExpressionEvaluator:
    """Avaliador seguro de expressões lógicas usando AST."""
    
    # Nós AST permitidos (apenas lógica e comparação básica)
    # Inclui nós de contexto (Load, Store, Del) que são inofensivos e aparecem em variáveis
    ALLOWED_NODES = {
        ast.Expression, ast.Compare, ast.Name, ast.Constant,
        ast.And, ast.Or, ast.Not, ast.UnaryOp, ast.BoolOp,
        ast.Eq, ast.NotEq, ast.Lt, ast.LtE, ast.Gt, ast.GtE,
        ast.USub, ast.UAdd,
        ast.Load, ast.Store, ast.Del  # Nós de contexto (inofensivos)
    }

    def evaluate(self, expression: str, context: dict[str, Any]) -> bool:
        """Avalia a expressão de forma segura contra o contexto fornecido."""
        try:
            # Analisa a expressão como uma árvore de sintaxe abstrata
            tree = ast.parse(expression, mode='eval')
        except SyntaxError as e:
            raise ValueError(f"Expressão com sintaxe inválida: {e}")
        
        return self._eval_node(tree.body, context)

    def _eval_node(self, node: ast.AST, context: dict[str, Any]) -> Any:
        """Avalia recursivamente os nós permitidos da AST."""
        if type(node) not in self.ALLOWED_NODES:
            raise SecurityError(f"Nó não permitido na expressão: {type(node).__name__}. Apenas comparações lógicas são permitidas.")

        if isinstance(node, ast.Constant):
            return node.value
        
        elif isinstance(node, ast.Name):
            if node.id not in context:
                raise ValueError(f"Variável desconhecida na regra: '{node.id}'. Variáveis disponíveis: {list(context.keys())}")
            return context[node.id]
        
        elif isinstance(node, ast.Compare):
            left = self._eval_node(node.left, context)
            for op, comparator in zip(node.ops, node.comparators):
                right = self._eval_node(comparator, context)

                # Dado nulo: comparacao nao avaliavel -> regra nao passa
                if left is None or right is None:
                    return False
                
                if isinstance(op, ast.Eq) and not (left == right): return False
                elif isinstance(op, ast.NotEq) and not (left != right): return False
                elif isinstance(op, ast.Lt) and not (left < right): return False
                elif isinstance(op, ast.LtE) and not (left <= right): return False
                elif isinstance(op, ast.Gt) and not (left > right): return False
                elif isinstance(op, ast.GtE) and not (left >= right): return False
                
                left = right  # Suporta comparações em cadeia: a < b < c
            return True
        
        elif isinstance(node, ast.BoolOp):
            if isinstance(node.op, ast.And):
                return all(self._eval_node(v, context) for v in node.values)
            elif isinstance(node.op, ast.Or):
                return any(self._eval_node(v, context) for v in node.values)
        
        elif isinstance(node, ast.UnaryOp):
            operand = self._eval_node(node.operand, context)
            if isinstance(node.op, ast.Not):
                return not operand
            if isinstance(node.op, ast.USub):
                return -operand
            if isinstance(node.op, ast.UAdd):
                return +operand
        
        raise SecurityError(f"Avaliação não suportada para o nó: {type(node).__name__}")


class RuleEvaluator:
    """Orquestra a avaliação de um conjunto de regras."""
    
    def __init__(self, rule_set: RuleSet):
        self.rule_set = rule_set
        self.safe_evaluator = SafeExpressionEvaluator()
    
    def evaluate(self, input_data: dict[str, Any]) -> list[dict[str, Any]]:
        """Avalia todas as regras ativas contra os dados de entrada."""
        results = []
        
        active_rules = [
            rule for rule in self.rule_set.rules 
            if rule.status == RuleStatus.ACTIVE
        ]
        
        # Ordenar por prioridade (menor número = mais prioritário)
        active_rules.sort(key=lambda r: r.priority)
        
        for rule in active_rules:
            try:
                result = self.safe_evaluator.evaluate(rule.expression, input_data)
                
                results.append({
                    'rule_id': rule.id,
                    'rule_version': rule.version,
                    'severity': rule.severity.value,
                    'passed': result,
                    'verdict': 'PASS' if result else 'FAIL',
                    'description': rule.description
                })
            except (ValueError, SecurityError, TypeError) as e:
                results.append({
                    'rule_id': rule.id,
                    'rule_version': rule.version,
                    'severity': rule.severity.value,
                    'passed': False,
                    'verdict': 'ERROR',
                    'error': str(e),
                    'description': rule.description
                })
        
        return results
