"""Conformal prediction para quantificação de incerteza."""
import numpy as np
from typing import List, Tuple, Dict, Any
from dataclasses import dataclass

@dataclass
class ConformalCalibration:
    """Resultado da calibração conformal."""
    alpha: float  # Nível de significância (ex: 0.1 para 90% coverage)
    quantile: float  # Quantil dos nonconformity scores
    n_calibration: int  # Número de pontos de calibração
    
@dataclass
class ConformalPrediction:
    """Predição com intervalo de confiança conformal."""
    point_prediction: Any
    prediction_set: List[Any]  # Conjunto de previsões
    confidence: float  # 1 - alpha
    
class ConformalPredictor:
    """
    Implementa conformal prediction para classificação.
    
    Método: split conformal prediction
    1. Divide dados em treino e calibração
    2. Treina modelo nos dados de treino
    3. Calcula nonconformity scores nos dados de calibração
    4. Usa quantil dos scores para construir prediction sets
    """
    
    def __init__(self, alpha: float = 0.1):
        """
        Args:
            alpha: Nível de significância (default: 0.1 = 90% coverage)
        """
        self.alpha = alpha
        self.calibration: ConformalCalibration = None
    
    def calculate_nonconformity_score(
        self, 
        prediction_proba: Dict[Any, float], 
        true_label: Any
    ) -> float:
        """
        Calcula nonconformity score para um ponto.
        
        Método: 1 - probabilidade da classe verdadeira
        Score alto = modelo está incerto sobre a classe verdadeira
        """
        if true_label not in prediction_proba:
            return 1.0  # Máxima não-conformidade
        
        return 1.0 - prediction_proba[true_label]
    
    def calibrate(
        self,
        calibration_predictions: List[Dict[Any, float]],
        calibration_labels: List[Any]
    ) -> ConformalCalibration:
        """
        Calibra o predictor usando dados de calibração.
        
        Args:
            calibration_predictions: Lista de probabilidades preditas
            calibration_labels: Labels verdadeiras
        
        Returns:
            ConformalCalibration com o quantil calculado
        """
        # Calcular nonconformity scores
        scores = [
            self.calculate_nonconformity_score(pred, label)
            for pred, label in zip(calibration_predictions, calibration_labels)
        ]
        
        # Calcular quantil ajustado
        n = len(scores)
        quantile_level = np.ceil((n + 1) * (1 - self.alpha)) / n
        quantile_level = min(quantile_level, 1.0)  # Cap at 1.0
        
        quantile_value = np.quantile(scores, quantile_level, method='higher')
        
        self.calibration = ConformalCalibration(
            alpha=self.alpha,
            quantile=quantile_value,
            n_calibration=n
        )
        
        return self.calibration
    
    def predict_set(self, prediction_proba: Dict[Any, float]) -> ConformalPrediction:
        """
        Gera prediction set para um novo ponto.
        
        Args:
            prediction_proba: Probabilidades preditas pelo modelo
        
        Returns:
            ConformalPrediction com point prediction e prediction set
        """
        if self.calibration is None:
            raise RuntimeError("Predictor not calibrated. Call calibrate() first.")
        
        # Point prediction: classe com maior probabilidade
        point_prediction = max(prediction_proba, key=prediction_proba.get)
        
        # Prediction set: todas as classes com score <= quantile
        prediction_set = []
        for label, proba in prediction_proba.items():
            score = 1.0 - proba
            if score <= self.calibration.quantile:
                prediction_set.append(label)
        
        return ConformalPrediction(
            point_prediction=point_prediction,
            prediction_set=prediction_set,
            confidence=1.0 - self.alpha
        )
    
    def get_calibration_summary(self) -> Dict[str, Any]:
        """Retorna resumo da calibração."""
        if self.calibration is None:
            return {"status": "not_calibrated"}
        
        return {
            "status": "calibrated",
            "alpha": self.calibration.alpha,
            "confidence": 1.0 - self.calibration.alpha,
            "quantile": round(self.calibration.quantile, 3),
            "n_calibration": self.calibration.n_calibration,
        }
