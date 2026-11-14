"""
Detetor de drift: Population Stability Index (PSI) para dados tabulares,
distância cosseno para embeddings. Thresholds configuráveis.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import numpy as np

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

class DriftReport:
    def __init__(self, feature: str, drift_score: float, threshold: float, 
                 drift_type: str, detected: bool, details: Dict[str, Any] = None):
        self.feature = feature
        self.drift_score = drift_score
        self.threshold = threshold
        self.drift_type = drift_type
        self.detected = detected
        self.details = details or {}
        self.timestamp = utc_now()
    
    def to_dict(self):
        return {
            "feature": self.feature,
            "drift_score": self.drift_score,
            "threshold": self.threshold,
            "drift_type": self.drift_type,
            "detected": self.detected,
            "details": self.details,
            "timestamp": self.timestamp.isoformat()
        }

class DriftDetector:
    """Deteta drift em dados tabulares e embeddings."""
    
    def __init__(self, psi_threshold: float = 0.2, cosine_threshold: float = 0.1):
        self.psi_threshold = psi_threshold
        self.cosine_threshold = cosine_threshold
        self.baseline: Dict[str, Any] = {}
    
    def set_baseline(self, baseline_data: Dict[str, Any]):
        """Define o baseline (referência) para comparação."""
        self.baseline = baseline_data
    
    def detect_tabular_drift(self, current_data: Dict[str, List], 
                              baseline_data: Dict[str, List]) -> List[DriftReport]:
        """
        Deteta drift em dados tabulares usando PSI (Population Stability Index).
        PSI > 0.2 = drift significativo.
        """
        reports = []
        
        for feature in baseline_data.keys():
            if feature not in current_data:
                continue
            
            baseline_values = baseline_data[feature]
            current_values = current_data[feature]
            
            # Calcular PSI
            psi = self._compute_psi(baseline_values, current_values)
            
            detected = psi > self.psi_threshold
            report = DriftReport(
                feature=feature,
                drift_score=psi,
                threshold=self.psi_threshold,
                drift_type="tabular_psi",
                detected=detected,
                details={"baseline_size": len(baseline_values), "current_size": len(current_values)}
            )
            reports.append(report)
        
        return reports
    
    def detect_embedding_drift(self, current_embeddings: np.ndarray, 
                               baseline_embeddings: np.ndarray) -> DriftReport:
        """
        Deteta drift em embeddings usando 1 - similaridade cosseno média.
        Score > 0.1 = drift significativo.
        """
        # Normalizar embeddings
        baseline_norm = baseline_embeddings / (np.linalg.norm(baseline_embeddings, axis=1, keepdims=True) + 1e-8)
        current_norm = current_embeddings / (np.linalg.norm(current_embeddings, axis=1, keepdims=True) + 1e-8)
        
        # Similaridade cosseno média (baseline vs current)
        similarities = []
        for curr in current_norm:
            sims = np.dot(baseline_norm, curr)
            similarities.append(np.max(sims))
        
        avg_similarity = np.mean(similarities)
        drift_score = 1.0 - avg_similarity  # Maior = mais drift
        
        detected = drift_score > self.cosine_threshold
        
        return DriftReport(
            feature="embeddings",
            drift_score=float(drift_score),
            threshold=self.cosine_threshold,
            drift_type="embedding_cosine",
            detected=detected,
            details={
                "avg_similarity": float(avg_similarity),
                "baseline_count": len(baseline_embeddings),
                "current_count": len(current_embeddings)
            }
        )
    
    def _compute_psi(self, baseline: List, current: List, bins: int = 10) -> float:
        """Calcula Population Stability Index."""
        if not baseline or not current:
            return 0.0
        
        try:
            # Calcular histogramas
            all_values = baseline + current
            min_val, max_val = min(all_values), max(all_values)
            
            if min_val == max_val:
                return 0.0
            
            bin_edges = np.linspace(min_val, max_val, bins + 1)
            
            baseline_hist, _ = np.histogram(baseline, bins=bin_edges)
            current_hist, _ = np.histogram(current, bins=bin_edges)
            
            # Converter para proporções (evitar divisão por zero)
            baseline_pct = (baseline_hist + 1e-6) / (len(baseline) + 1e-6 * bins)
            current_pct = (current_hist + 1e-6) / (len(current) + 1e-6 * bins)
            
            # PSI = sum((current - baseline) * ln(current / baseline))
            psi = np.sum((current_pct - baseline_pct) * np.log(current_pct / baseline_pct))
            
            return float(psi)
        except Exception:
            return 0.0
