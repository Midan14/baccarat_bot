# core/ml_prediction_engine.py
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from typing import List, Dict, Tuple, Any
import joblib
import os
from dataclasses import dataclass
from utils.logger import logger

@dataclass
class PredictionResult:
    """Resultado de la predicción para el motor de decisiones"""
    signal: str  # 'B', 'P', 'E', 'NONE'
    confidence: float
    algorithm: str
    probabilities: Dict[str, float]

class MLFeaturesEngine:
    """Motor de features avanzados para ML"""
    
    @staticmethod
    def generate_features(history: List[str],
                         window_sizes=None) -> np.ndarray:
        """Generar features estadísticos complejos"""
        if window_sizes is None:
            window_sizes = [10, 20, 50]
        features = []
        
        for window in window_sizes:
            if len(history) < window:
                continue
                
            recent = history[-window:]
            
            # 1. Features de frecuencia
            dragon_freq = recent.count('Dragon') / window
            tiger_freq = recent.count('Tiger') / window
            tie_freq = recent.count('Tie') / window
            
            # 2. Features de rachas (streaks)
            max_streak = 0
            current_streak = 1
            last_outcome = recent[0]
            
            for outcome in recent[1:]:
                if outcome == last_outcome:
                    current_streak += 1
                    max_streak = max(max_streak, current_streak)
                else:
                    current_streak = 1
                    last_outcome = outcome
            
            # 3. Features de entropía (indica aleatoriedad)
            from scipy import stats
            probs = [dragon_freq, tiger_freq, tie_freq]
            entropy = stats.entropy(probs)
            
            # 4. Features de autocorrelación (lag 1,2,3)
            autocorr_lag1 = MLFeaturesEngine._autocorrelation(recent, 1)
            autocorr_lag2 = MLFeaturesEngine._autocorrelation(recent, 2)
            autocorr_lag3 = MLFeaturesEngine._autocorrelation(recent, 3)
            
            # 5. Features de cambios de dirección
            direction_changes = sum(
                1 for i in range(1, len(recent) - 1) 
                if (recent[i] != recent[i-1]) and (recent[i] != recent[i+1])
            )
            
            # 6. Features de ritmo (timing)
            timing_variance = np.var([i for i, x in enumerate(recent)
                                     if x == 'Tie']) if 'Tie' in recent else 0
            
            features.extend([
                dragon_freq, tiger_freq, tie_freq,
                max_streak, current_streak,
                entropy,
                autocorr_lag1, autocorr_lag2, autocorr_lag3,
                direction_changes / window,
                timing_variance
            ])
        
        return np.array(features).reshape(1, -1)
    
    @staticmethod
    def _autocorrelation(arr: List[str], lag: int) -> float:
        """Calcular autocorrelación para series temporales categóricas"""
        if len(arr) < lag + 1:
            return 0
        arr_num = np.array([0 if x == 'Dragon' else 1 if x == 'Tiger' else 2
                           for x in arr])
        correlation = np.corrcoef(arr_num[:-lag], arr_num[lag:])[0, 1]
        return correlation if not np.isnan(correlation) else 0

class MLRandomForestEngine:
    """Motor de predicción con Random Forest"""
    
    def __init__(self, model_path="models/rf_model.pkl"):
        self.model_path = model_path
        self.model = None
        self.scaler = StandardScaler()
        self.feature_names = []
        self._load_or_train_model()
    
    def _load_or_train_model(self):
        """Cargar modelo existente o entrenar uno nuevo"""
        if os.path.exists(self.model_path):
            self.model = joblib.load(self.model_path)
            logger.info("Modelo Random Forest cargado")
        else:
            logger.info("No se encontró modelo, usará predicción básica "
                       "hasta entrenamiento")
    
    def train_model(self, historical_data: List[str], outcomes: List[str]):
        """Entrenar modelo con datos históricos"""
        from sklearn.model_selection import train_test_split
        
        X, y = [], []
        for i in range(60, len(historical_data)):
            features = MLFeaturesEngine.generate_features(historical_data[:i])
            X.append(features.flatten())
            y.append(outcomes[i])
        
        X = np.vstack(X)
        y = np.array(y)
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2)
        
        self.model = RandomForestClassifier(
            n_estimators=200,
            max_depth=15,
            min_samples_split=10,
            min_samples_leaf=5,
            class_weight='balanced',
            random_state=42
        )
        
        X_train_scaled = self.scaler.fit_transform(X_train)
        self.model.fit(X_train_scaled, y_train)
        
        # Evaluar
        from sklearn.metrics import accuracy_score, classification_report
        X_test_scaled = self.scaler.transform(X_test)
        y_pred = self.model.predict(X_test_scaled)
        
        logger.info(f"Modelo entrenado - Accuracy: "
                   f"{accuracy_score(y_test, y_pred):.3f}")
        logger.info(f"Reporte:\n{classification_report(y_test, y_pred)}")
        
        # Guardar modelo
        os.makedirs("models", exist_ok=True)
        joblib.dump(self.model, self.model_path)
        joblib.dump(self.scaler, "models/scaler.pkl")
    
    def predict(self, history: List[str]) -> Tuple[str, float, Dict[str, float]]:
        """Predicción con probabilidades y confianza"""
        if len(history) < 60 or self.model is None:
            return "NONE", 0.0, {}
        
        features = MLFeaturesEngine.generate_features(history)
        features_scaled = self.scaler.transform(features)
        
        # Obtener probabilidades de cada clase
        proba = self.model.predict_proba(features_scaled)[0]
        classes = self.model.classes_
        
        prob_dict = dict(zip(classes, proba))
        best_pred = max(prob_dict.keys(), key=lambda k: prob_dict[k])
        confidence = prob_dict[best_pred]
        
        # Calcular confianza relativa (entropy inversa)
        from scipy import stats
        relative_confidence = 1 - (stats.entropy(proba) / np.log(len(classes)))
        
        return best_pred, confidence * relative_confidence, prob_dict

# Clase principal para mantener compatibilidad con el main.py
class PredictionEngine:
    """Wrapper para MLRandomForestEngine con interfaz estándar"""
    
    def __init__(self):
        self.ml_engine = MLRandomForestEngine()
    
    def analyze(self, history: List[str]) -> PredictionResult:
        """Analizar historial y devolver predicción en formato estándar"""
        prediction, confidence, probabilities = self.ml_engine.predict(history)
        
        # Convertir predicción a formato estándar (B, P, E)
        signal_map = {
            'Dragon': 'B',
            'Tiger': 'P',
            'Tie': 'E',
            'NONE': 'NONE'
        }
        standard_signal = signal_map.get(prediction, 'NONE')
        
        return PredictionResult(
            signal=standard_signal,
            confidence=confidence,
            algorithm='ml_random_forest',
            probabilities=probabilities
        )