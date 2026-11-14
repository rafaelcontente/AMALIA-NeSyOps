import re
from decimal import Decimal, InvalidOperation
from datetime import datetime

def normalize_currency(value_str: str) -> Decimal:
    cleaned = value_str.replace("€", "").replace("$", "").strip().replace(".", "").replace(",", ".")
    try:
        return Decimal(cleaned)
    except InvalidOperation:
        raise ValueError(f"Valor monetário inválido: {value_str}")

def normalize_date(date_str: str) -> datetime:
    date_str = re.sub(r'\s+', ' ', date_str).strip().lower()
    
    # Mapeamento para garantir funcionamento independente do locale do macOS/Linux
    pt_to_en = {
        "janeiro": "january", "fevereiro": "february", "março": "march", "abril": "april",
        "maio": "may", "junho": "june", "julho": "july", "agosto": "august",
        "setembro": "september", "outubro": "october", "novembro": "november", "dezembro": "december",
        "jan": "jan", "fev": "feb", "mar": "mar", "abr": "apr", "mai": "may", "jun": "jun",
        "jul": "jul", "ago": "aug", "set": "sep", "out": "oct", "nov": "nov", "dez": "dec"
    }
    for pt, en in pt_to_en.items():
        date_str = date_str.replace(pt, en)
    
    formats = ["%d/%m/%Y", "%d-%m-%Y", "%d de %B de %Y", "%d de %b de %Y"]
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    raise ValueError(f"Formato de data não suportado: {date_str}")

def normalize_text(text: str) -> str:
    text = re.sub(r'\s+', ' ', text).strip()
    return text.replace("“", '"').replace("”", '"').replace("‘", "'").replace("’", "'")
