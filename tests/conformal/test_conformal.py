"""Testes para conformal prediction."""
import pytest
import numpy as np
from conformal import ConformalPredictor

@pytest.fixture
def simple_model_predictions():
    """Gera predições sintéticas para teste."""
    np.random.seed(42)
    classes = ["approved", "rejected"]
    
    # Dados de calibração (30 pontos)
    calibration_preds = []
    calibration_labels = []
    for _ in range(30):
        true_label = np.random.choice(classes)
        if np.random.random() < 0.8:
            proba = {true_label: 0.7 + np.random.random() * 0.2}
            other = [c for c in classes if c != true_label][0]
            proba[other] = 1.0 - proba[true_label]
        else:
            wrong_label = [c for c in classes if c != true_label][0]
            proba = {wrong_label: 0.6 + np.random.random() * 0.2}
            proba[true_label] = 1.0 - proba[wrong_label]
        
        calibration_preds.append(proba)
        calibration_labels.append(true_label)
    
    # Dados de teste (20 pontos)
    test_preds = []
    test_labels = []
    for _ in range(20):
        true_label = np.random.choice(classes)
        if np.random.random() < 0.8:
            proba = {true_label: 0.7 + np.random.random() * 0.2}
            other = [c for c in classes if c != true_label][0]
            proba[other] = 1.0 - proba[true_label]
        else:
            wrong_label = [c for c in classes if c != true_label][0]
            proba = {wrong_label: 0.6 + np.random.random() * 0.2}
            proba[true_label] = 1.0 - proba[wrong_label]
        
        test_preds.append(proba)
        test_labels.append(true_label)
    
    return calibration_preds, calibration_labels, test_preds, test_labels

def test_conformal_calibration(simple_model_predictions):
    """Testa calibração conformal."""
    cal_preds, cal_labels, _, _ = simple_model_predictions
    
    predictor = ConformalPredictor(alpha=0.1)
    calibration = predictor.calibrate(cal_preds, cal_labels)
    
    assert calibration.alpha == 0.1
    assert calibration.n_calibration == 30
    assert 0.0 <= calibration.quantile <= 1.0
    
    summary = predictor.get_calibration_summary()
    assert summary["status"] == "calibrated"
    assert summary["confidence"] == 0.9

def test_conformal_prediction_set(simple_model_predictions):
    """Testa geração de prediction sets."""
    cal_preds, cal_labels, test_preds, test_labels = simple_model_predictions
    
    predictor = ConformalPredictor(alpha=0.1)
    predictor.calibrate(cal_preds, cal_labels)
    
    predictions = [predictor.predict_set(pred) for pred in test_preds]
    
    # Verificar cobertura empírica
    covered = sum(
        1 for pred, label in zip(predictions, test_labels)
        if label in pred.prediction_set
    )
    coverage = covered / len(test_labels)
    
    # Cobertura deve ser aproximadamente 90% (±10% devido a variância)
    assert 0.7 <= coverage <= 1.0, f"Coverage {coverage:.2f} outside [0.7, 1.0]"
    
    print(f"\nCoverage: {coverage:.2%} (expected ~90%)")
    print(f"Average set size: {np.mean([len(p.prediction_set) for p in predictions]):.2f}")

def test_conformal_prediction_set_not_empty(simple_model_predictions):
    """Verifica que prediction sets nunca estão vazios."""
    cal_preds, cal_labels, test_preds, _ = simple_model_predictions
    
    predictor = ConformalPredictor(alpha=0.1)
    predictor.calibrate(cal_preds, cal_labels)
    
    predictions = [predictor.predict_set(pred) for pred in test_preds]
    
    for pred in predictions:
        assert len(pred.prediction_set) > 0, "Prediction set cannot be empty"
        assert pred.point_prediction in pred.prediction_set

def test_conformal_uncalibrated_raises():
    """Testa que predict_set falha sem calibração."""
    predictor = ConformalPredictor(alpha=0.1)
    
    with pytest.raises(RuntimeError, match="not calibrated"):
        predictor.predict_set({"approved": 0.8, "rejected": 0.2})

def test_conformal_high_confidence(simple_model_predictions):
    """Testa conformal com alta confiança (alpha=0.05)."""
    cal_preds, cal_labels, test_preds, test_labels = simple_model_predictions
    
    predictor = ConformalPredictor(alpha=0.05)  # 95% coverage
    predictor.calibrate(cal_preds, cal_labels)
    
    predictions = [predictor.predict_set(pred) for pred in test_preds]
    
    # Sets devem ser maiores (mais conservadores)
    avg_set_size = np.mean([len(p.prediction_set) for p in predictions])
    assert avg_set_size >= 1.5, f"Sets too small for 95% confidence: {avg_set_size:.2f}"

def test_conformal_low_confidence(simple_model_predictions):
    """Testa conformal com baixa confiança (alpha=0.3)."""
    cal_preds, cal_labels, test_preds, test_labels = simple_model_predictions
    
    predictor = ConformalPredictor(alpha=0.3)  # 70% coverage
    predictor.calibrate(cal_preds, cal_labels)
    
    predictions = [predictor.predict_set(pred) for pred in test_preds]
    
    # Sets devem ser menores (menos conservadores)
    avg_set_size = np.mean([len(p.prediction_set) for p in predictions])
    assert avg_set_size <= 1.8, f"Sets too large for 70% confidence: {avg_set_size:.2f}"
