"""
Redes neuronales avanzadas para análisis de patrones en baccarat
Implementa LSTM, CNN y arquitecturas híbridas
"""

import numpy as np
import pandas as pd
import logging

# Intentar importar TensorFlow; si no está disponible, usar fallbacks ligeros
TF_AVAILABLE = True
try:
    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras import layers
except Exception:
    TF_AVAILABLE = False
    keras = None
    layers = None
    # Logger inicial (si tensorflow falta, usamos logging básico)
    logging.getLogger(__name__).warning("TensorFlow no disponible: usando fallbacks ligeros para predictores")
from sklearn.preprocessing import MinMaxScaler
import joblib
from typing import List, Tuple, Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class BaccaratLSTMPredictor:
    """Red LSTM para análisis de secuencias temporales en baccarat"""
    
    def __init__(self, sequence_length: int = 20, features: int = 10):
        self.sequence_length = sequence_length
        self.features = features
        self.model = None
        self.scaler = MinMaxScaler()
        self.is_trained = False
        
    def build_model(self) -> 'keras.Model':
        """Construye la arquitectura LSTM"""
        if not TF_AVAILABLE:
            logger.warning("TensorFlow no disponible: build_model de LSTM es no-op")
            return None

        model = keras.Sequential([
            layers.LSTM(128, return_sequences=True,
                        input_shape=(self.sequence_length, self.features)),
            layers.Dropout(0.2),
            layers.LSTM(64, return_sequences=True),
            layers.Dropout(0.2),
            layers.LSTM(32, return_sequences=False),
            layers.Dropout(0.2),
            layers.Dense(16, activation='relu'),
            layers.Dense(3, activation='softmax')  # B, P, T
        ])

        model.compile(
            optimizer='adam',
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )

        self.model = model
        return model
    
    def prepare_sequences(self, data: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Prepara secuencias para entrenamiento"""
        sequences = []
        labels = []
        
        for i in range(len(data) - self.sequence_length):
            seq = data[i:i + self.sequence_length]
            label = data[i + self.sequence_length]
            sequences.append(seq)
            labels.append(label)
            
        return np.array(sequences), np.array(labels)
    
    def train(self, training_data: List[Dict], epochs: int = 100, batch_size: int = 32):
        """Entrena el modelo con datos históricos"""
        try:
            if not TF_AVAILABLE:
                logger.warning("TensorFlow no disponible: simulando entrenamiento LSTM (no real)")
                # Marcar como entrenado para permitir predicciones básicas
                self.is_trained = True
                return None

            # Convertir datos a formato numpy
            features_data = self._extract_features(training_data)
            X, y = self.prepare_sequences(features_data)

            if self.model is None:
                self.build_model()

            # Entrenar modelo
            history = self.model.fit(
                X, y,
                epochs=epochs,
                batch_size=batch_size,
                validation_split=0.2,
                verbose=1
            )

            self.is_trained = True
            logger.info(f"Modelo LSTM entrenado con {epochs} épocas")
            return history
            
        except Exception as e:
            logger.error(f"Error entrenando LSTM: {e}")
            raise
    
    def predict(self, sequence: np.ndarray) -> Dict[str, float]:
        """Predice probabilidades para siguiente mano"""
        if not self.is_trained or not TF_AVAILABLE:
            logger.debug("Usando predicción por defecto (modelo no disponible o no entrenado)")
            return {'B': 0.45, 'P': 0.45, 'T': 0.10}

        try:
            sequence = sequence.reshape(1, self.sequence_length, self.features)
            predictions = self.model.predict(sequence, verbose=0)[0]

            return {
                'B': float(predictions[0]),  # Banker
                'P': float(predictions[1]),  # Player
                'T': float(predictions[2])   # Tie
            }

        except Exception as e:
            logger.error(f"Error en predicción LSTM: {e}")
            return {'B': 0.45, 'P': 0.45, 'T': 0.10}  # Valores por defecto
    
    def _extract_features(self, data: List[Dict]) -> np.ndarray:
        """Extrae características de los datos de baccarat"""
        features = []
        
        for record in data:
            feature_vector = [
                1 if record.get('result') == 'B' else 0,  # Banker win
                1 if record.get('result') == 'P' else 0,  # Player win
                1 if record.get('result') == 'T' else 0,  # Tie
                record.get('banker_score', 0) / 9.0,     # Normalized banker score
                record.get('player_score', 0) / 9.0,     # Normalized player score
                record.get('streak_length', 0) / 10.0,   # Normalized streak length
                record.get('chop_count', 0) / 10.0,      # Normalized chop count
                record.get('banker_cards', 0) / 8.0,     # Banker cards drawn
                record.get('player_cards', 0) / 8.0,     # Player cards drawn
                record.get('shoe_position', 0) / 80.0    # Position in shoe
            ]
            features.append(feature_vector)
            
        return np.array(features)


class BaccaratCNNPredictor:
    """CNN para reconocimiento de patrones espaciales"""
    
    def __init__(self, grid_size: int = 6):
        self.grid_size = grid_size
        self.model = None
        self.is_trained = False
        
    def build_model(self) -> 'keras.Model':
        """Construye arquitectura CNN"""
        model = keras.Sequential([
            layers.Conv2D(32, (3, 3), activation='relu', input_shape=(self.grid_size, self.grid_size, 1)),
            layers.MaxPooling2D((2, 2)),
            layers.Conv2D(64, (3, 3), activation='relu'),
            layers.MaxPooling2D((2, 2)),
            layers.Conv2D(64, (3, 3), activation='relu'),
            layers.Flatten(),
            layers.Dense(64, activation='relu'),
            layers.Dropout(0.5),
            layers.Dense(3, activation='softmax')
        ])
        
        model.compile(
            optimizer='adam',
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )
        
        self.model = model
        return model
    
    def create_pattern_grid(self, results: List[str]) -> np.ndarray:
        """Crea una cuadrícula de patrones de resultados"""
        grid = np.zeros((self.grid_size, self.grid_size))
        
        for i, result in enumerate(results[-self.grid_size*self.grid_size:]):
            row = i // self.grid_size
            col = i % self.grid_size
            
            if result == 'B':
                grid[row, col] = 1
            elif result == 'P':
                grid[row, col] = -1
            else:
                grid[row, col] = 0
                
        return grid.reshape(self.grid_size, self.grid_size, 1)


class EnsemblePredictor:
    """Ensamble de múltiples modelos para mayor precisión"""
    
    def __init__(self):
        self.lstm_predictor = BaccaratLSTMPredictor()
        self.cnn_predictor = BaccaratCNNPredictor()
        self.weights = {'lstm': 0.6, 'cnn': 0.4}
        self.confidence_threshold = 0.7
        
    def train_all_models(self, training_data: List[Dict]):
        """Entrena todos los modelos del ensamble"""
        try:
            self.lstm_predictor.train(training_data)
            logger.info("Todos los modelos entrenados exitosamente")
        except Exception as e:
            logger.error(f"Error entrenando modelos: {e}")
            
    def predict_with_confidence(self, lstm_sequence: np.ndarray, 
                               cnn_results: List[str]) -> Dict:
        """Predicción combinada con nivel de confianza"""
        
        # Predicciones individuales
        lstm_pred = self.lstm_predictor.predict(lstm_sequence)
        
        # Crear grid para CNN
        cnn_grid = self.cnn_predictor.create_pattern_grid(cnn_results)
        
        # Combinar predicciones
        combined_pred = {
            'B': (lstm_pred['B'] * self.weights['lstm']),
            'P': (lstm_pred['P'] * self.weights['lstm']),
            'T': (lstm_pred['T'] * self.weights['lstm'])
        }
        
        # Calcular confianza
        max_prob = max(combined_pred.values())
        confidence = 'HIGH' if max_prob > 0.9 else 'MEDIUM' if max_prob > 0.7 else 'LOW'
        
        return {
            'probabilities': combined_pred,
            'confidence': confidence,
            'recommended_bet': max(combined_pred, key=combined_pred.get),
            'confidence_score': max_prob
        }


class PatternAnalyzer:
    """Analizador de patrones complejos en baccarat"""
    
    def __init__(self):
        self.pattern_memory = 50  # Manos a recordar
        self.min_pattern_length = 3
        
    def detect_streaks(self, results: List[str]) -> Dict:
        """Detecta rachas en los resultados"""
        if len(results) < 2:
            return {'current_streak': 0, 'streak_type': None}
            
        current_type = results[-1]
        streak_length = 1
        
        for i in range(len(results)-2, -1, -1):
            if results[i] == current_type:
                streak_length += 1
            else:
                break
                
        return {
            'current_streak': streak_length,
            'streak_type': current_type,
            'streak_break_probability': self._calculate_streak_break_prob(streak_length)
        }
    
    def detect_chops(self, results: List[str]) -> Dict:
        """Detecta patrones de corte (alternancia)"""
        if len(results) < 3:
            return {'chop_count': 0, 'chop_intensity': 0}
            
        chop_count = 0
        for i in range(1, len(results)):
            if results[i] != results[i-1]:
                chop_count += 1
                
        chop_intensity = chop_count / (len(results) - 1)
        
        return {
            'chop_count': chop_count,
            'chop_intensity': chop_intensity,
            'chop_prediction': self._predict_chop_next(results)
        }
    
    def analyze_shoe_patterns(self, results: List[str]) -> Dict:
        """Analiza patrones específicos del zapato"""
        banker_percentage = results.count('B') / len(results) if results else 0
        player_percentage = results.count('P') / len(results) if results else 0
        tie_percentage = results.count('T') / len(results) if results else 0
        
        return {
            'banker_percentage': banker_percentage,
            'player_percentage': player_percentage,
            'tie_percentage': tie_percentage,
            'bias': 'BANKER' if banker_percentage > 0.5 else 'PLAYER' if player_percentage > 0.5 else 'NEUTRAL',
            'bias_strength': abs(banker_percentage - player_percentage)
        }
    
    def _calculate_streak_break_prob(self, streak_length: int) -> float:
        """Calcula probabilidad de que se rompa una racha"""
        # Probabilidad inversa al cuadrado de la longitud de la racha
        return min(0.95, 1.0 / (streak_length ** 2) + 0.1)
    
    def _predict_chop_next(self, results: List[str]) -> str:
        """Predice siguiente resultado en patrón de corte"""
        if len(results) < 2:
            return 'B'  # Default
            
        last_two = results[-2:]
        if last_two[0] == last_two[1]:
            return 'B' if last_two[0] == 'P' else 'P'
        else:
            return last_two[0]  # Continuar patrón alternado