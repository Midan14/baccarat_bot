# core/anomaly_detector.py
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import numpy as np
from typing import List, Dict

class GameAnomalyDetector:
    """Detectar situaciones anómalas que invaliden predicciones"""
    
    def __init__(self):
        self.model = IsolationForest(
            contamination=0.1,
            random_state=42,
            n_estimators=100
        )
        self.scaler = StandardScaler()
        self.is_fitted = False
    
    def fit(self, normal_game_data: List[List[float]]):
        """
        Entrenar con datos de "juego normal"
        Cada muestra: [freq_dragon, freq_tiger, volatility, entropy, ...]
        """
        X = np.array(normal_game_data) if len(normal_game_data) > 0 else np.random.rand(100, 5)
        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled)
        self.is_fitted = True
    
    def detect_anomaly(self, current_features: List[float]) -> Dict[str, any]:
        """
        Detectar si el estado actual es anómalo
        """
        if not self.is_fitted:
            return {'is_anomaly': False, 'score': 0, 'reason': 'Modelo no entrenado'}
        
        X = np.array(current_features).reshape(1, -1)
        X_scaled = self.scaler.transform(X)
        
        # Isolation Forest score (-1 = anomalia, 1 = normal)
        anomaly_score = self.model.decision_function(X_scaled)
        is_anomaly = self.model.predict(X_scaled)[0] == -1
        
        # Calcular features específicos de anomalía
        reasons = []
        if current_features[0] > 0.7:  # Dragon frequency too high
            reasons.append(f"Frecuencia Dragon anormal: {current_features[0]:.2%}")
        if current_features[2] > 1.5:  # Volatility too high
            reasons.append(f"Volatilidad extrema: {current_features[2]:.2f}")
        
        return {
            'is_anomaly': is_anomaly,
            'anomaly_score': float(anomaly_score),
            'reasons': reasons,
            'should_stop': is_anomaly and len(reasons) >= 2
        }

# Uso en el bucle principal
anomaly_detector = GameAnomalyDetector()

# En cada iteración:
features = [
    game_state['history'].count('Dragon') / len(game_state['history']),
    game_state['history'].count('Tiger') / len(game_state['history']),
    validator.volatility_analysis(game_state['history'])['volatility'],
    entropy  # calculado previamente
]

anomaly_result = anomaly_detector.detect_anomaly(features)
if anomaly_result['should_stop']:
    logger.critical(f"ANOMALÍA DETECTADA: {anomaly_result['reasons']}")
    return BettingDecision(False, '', 0, 0, '', "Condiciones anómalas - STOP")