from typing import List, Dict, Any

class LLMProposer:
    def __init__(self, responses: List[Dict[str, Any]] = None):
        self.responses = responses or []
        self.call_count = 0

    def propose_rule(self, normative_text: str) -> Dict[str, Any]:
        if self.call_count < len(self.responses):
            response = self.responses[self.call_count]
            self.call_count += 1
            return response
        
        self.call_count += 1
        return {
            "expression": "syntax_error((",
            "test_cases": [],
            "explanation": "LLM falhou em gerar regra válida."
        }

    def reset(self):
        self.call_count = 0
