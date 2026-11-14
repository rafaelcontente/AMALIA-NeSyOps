"""
Segurança de ingestão: deteta instruções embutidas em documentos.
Regra: todo o texto ingerido é dado não confiável.
"""
import re
from typing import Tuple

INJECTION_PATTERNS = [
    # Originais (mantidos para compatibilidade)
    r"ignora (as )?instruções",
    r"ignora (as )?regras",
    r"esquece (as )?instruções",
    r"esquece (as )?regras",
    r"ignore previous instructions",
    r"disregard (the )?rules",
    r"system prompt",
    r"atue como se",
    # Alargamento: variantes PT/EN, jailbreak, XSS, SQL
    r"ignor[ea] (as )?(instruções|regras)",
    r"esquec[ea] (as )?(instruções|regras)",
    r"ignore (all |any |the )?(previous|prior|above) instructions",
    r"disregard (all |the |your )?(rules|instructions)",
    r"forget (all |your |the |previous )?(rules|instructions)",
    r"(?:^|\n)\s*system\s*:",
    r"developer mode",
    r"you are now dan\b",
    r"do anything now",
    r"<\s*script",
    r"\bdrop\s+table\b",
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
