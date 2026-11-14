"""
Segurança de ingestão: deteta instruções embutidas em documentos.
Regra: todo o texto ingerido é dado não confiável.
"""
import re
from typing import Tuple

INJECTION_PATTERNS = [
    r"ignora (as )?instruções",
    r"ignora (as )?regras",
    r"esquece (as )?instruções",
    r"esquece (as )?regras",
    r"ignore previous instructions",
    r"disregard (the )?rules",
    r"system prompt",
    r"atue como se"
]

def check_prompt_injection(text: str) -> Tuple[bool, str]:
    """
    Verifica se o texto contém tentativas de prompt injection.
    Retorna (detetado, motivo).
    """
    text_lower = text.lower()
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, text_lower):
            return True, f"Padrão de injection detetado: {pattern}"
    return False, ""
