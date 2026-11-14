"""
Funções de criptografia: hash, assinatura digital e verificação.
"""
import hashlib
import json
from typing import Dict, Any, List
from datetime import datetime

def compute_sha256(data: str) -> str:
    """Calcula SHA256 de uma string."""
    return hashlib.sha256(data.encode()).hexdigest()

def sign_chain(entries: List[Dict[str, Any]], private_key: str = "mock-key") -> str:
    """
    Assina digitalmente a cadeia de entradas.
    Em produção, usar criptografia assimétrica real (RSA/ECDSA).
    """
    # Concatenar todos os hashes
    chain_data = "".join([e.get("entry_hash", "") for e in entries])
    
    # Assinar (mock: hash da concatenação + chave)
    signature_input = chain_data + private_key
    signature = compute_sha256(signature_input)
    
    return signature

def verify_signature(entries: List[Dict[str, Any]], signature: str, 
                     private_key: str = "mock-key") -> bool:
    """Verifica a assinatura da cadeia."""
    expected_signature = sign_chain(entries, private_key)
    return signature == expected_signature

def pseudonymize_data(data: Dict[str, Any], salt: str = "rgpd-salt") -> str:
    """
    Pseudonimiza dados pessoais (RGPD).
    Retorna um hash irreversível dos dados sensíveis.
    """
    # Identificar campos sensíveis (exemplo: nome, email, nif)
    sensitive_fields = ["nome", "email", "nif", "morada", "telefone"]
    
    sensitive_data = {k: v for k, v in data.items() if k.lower() in sensitive_fields}
    
    if not sensitive_data:
        return ""
    
    json_str = json.dumps(sensitive_data, sort_keys=True)
    return compute_sha256(json_str + salt)
