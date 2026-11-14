"""
Parsers de documentos (PDF, DOCX, HTML, OCR).
Preparado para integrar IBM Docling, Firecrawl e Tesseract.
Por enquanto, usa implementação base para validação da arquitetura.
"""
import hashlib
from pathlib import Path
from typing import List, Dict, Any

def compute_hash(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()

def parse_document(file_path: str) -> List[Dict[str, Any]]:
    """
    Simula a extração de fragmentos de um documento.
    Na produção, isto chamará IBM Docling (PDF/DOCX) ou Firecrawl (HTML).
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Documento não encontrado: {file_path}")
    
    content = path.read_text(encoding="utf-8")
    doc_hash = compute_hash(content)
    
    # Simula fragmentos por página
    return [{
        "doc_id": path.stem,
        "page": 1,
        "content": content,
        "hash": doc_hash,
        "source": str(path)
    }]
