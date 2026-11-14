from typing import List, Dict, Any
from formalize.proposer import LLMProposer
from formalize.compiler import RuleCompiler
from policy.models import Rule, RuleTestCase, RuleStatus, RuleSeverity
from policy.registry import RuleRegistry

class FormalizationPipeline:
    def __init__(self, registry: RuleRegistry, max_retries: int = 3):
        self.registry = registry
        self.compiler = RuleCompiler()
        self.max_retries = max_retries

    def formalize(self, normative_text: str, proposer: LLMProposer, rule_name: str, author: str) -> Rule:
        last_error = None
        
        for attempt in range(1, self.max_retries + 1):
            proposal = proposer.propose_rule(normative_text)
            expression = proposal.get("expression", "")
            test_cases_data = proposal.get("test_cases", [])
            
            try:
                self.compiler.compile(expression)
            except ValueError as e:
                last_error = f"Tentativa {attempt}: {str(e)}"
                continue
            
            test_cases = []
            for tc in test_cases_data:
                test_cases.append(RuleTestCase(
                    input_data=tc["input"],
                    expected_result=tc["expected"],
                    description=tc.get("description", "")
                ))
            
            rule = Rule(
                name=rule_name,
                version="0.1.0",
                description=f"Gerada de: {normative_text[:50]}...",
                severity=RuleSeverity.HARD,
                author=author,
                expression=expression,
                test_cases=test_cases,
                status=RuleStatus.DRAFT,
                source_text=normative_text
            )
            
            self.registry.create_rule(rule)
            return rule
        
        raise RuntimeError(f"Falha na formalização após {self.max_retries} tentativas. Último erro: {last_error}")
