"""
Sistema avanzado de generación de señales con confianza graduada
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import json
import time
from datetime import datetime, timedelta
import logging

from .neural_networks import EnsemblePredictor, PatternAnalyzer
from .monte_carlo import MonteCarloEngine, BayesianUpdater
from .data_acquisition import GameData

logger = logging.getLogger(__name__)

class ConfidenceLevel(Enum):
    """Niveles de confianza para señales"""
    HIGH = "HIGH"      # 90-98%
    MEDIUM = "MEDIUM"  # 70-89%
    LOW = "LOW"        # <70%

@dataclass
class Signal:
    """Estructura de señal de apuesta"""
    timestamp: datetime
    table_id: str
    confidence: ConfidenceLevel
    recommended_bet: str  # B, P, T
    confidence_score: float  # 0-1
    bet_size: int  # 1-7 unidades
    reasoning: Dict  # Razón de la recomendación
    pattern_analysis: Dict  # Análisis de patrones
    monte_carlo_probs: Dict  # Probabilidades Monte Carlo
    neural_network_probs: Dict  # Probabilidades redes neuronales
    expected_value: float
    risk_level: str  # LOW, MEDIUM, HIGH
    
    def to_dict(self) -> Dict:
        """Convierte señal a diccionario"""
        return {
            'timestamp': self.timestamp.isoformat(),
            'table_id': self.table_id,
            'confidence': self.confidence.value,
            'recommended_bet': self.recommended_bet,
            'confidence_score': self.confidence_score,
            'bet_size': self.bet_size,
            'reasoning': self.reasoning,
            'pattern_analysis': self.pattern_analysis,
            'monte_carlo_probs': self.monte_carlo_probs,
            'neural_network_probs': self.neural_network_probs,
            'expected_value': self.expected_value,
            'risk_level': self.risk_level
        }

class SignalGenerator:
    """Generador principal de señales de alta precisión"""
    
    def __init__(self):
        self.ensemble_predictor = EnsemblePredictor()
        self.pattern_analyzer = PatternAnalyzer()
        self.monte_carlo = MonteCarloEngine(num_simulations=50000)
        self.bayesian = BayesianUpdater()
        
        # Configuración de confianza
        self.confidence_thresholds = {
            'HIGH': 0.90,
            'MEDIUM': 0.70,
            'LOW': 0.50
        }
        
        # Configuración de apuestas
        self.bet_sizes = {
            'HIGH': {'min': 5, 'max': 7},
            'MEDIUM': {'min': 2, 'max': 4},
            'LOW': {'min': 0, 'max': 1}  # 0 = no apostar
        }
        
        # Historial para análisis
        self.history: List[GameData] = []
        self.max_history_size = 1000
        
        # Estadísticas de rendimiento
        self.signal_stats = {
            'total_signals': 0,
            'high_confidence_signals': 0,
            'success_rate': 0.0,
            'profit_loss': 0.0
        }
        
    def add_game_data(self, game_data: GameData):
        """Agrega nuevo dato de juego"""
        self.history.append(game_data)
        
        # Mantener tamaño del historial
        if len(self.history) > self.max_history_size:
            self.history.pop(0)
            
    def generate_signal(self, current_game: GameData) -> Optional[Signal]:
        """Genera señal de apuesta basada en análisis completo"""
        
        try:
            # 1. Análisis de patrones
            pattern_analysis = self._analyze_current_patterns()
            
            # 2. Predicción con redes neuronales
            neural_pred = self._get_neural_prediction()
            
            # 3. Simulación Monte Carlo
            monte_carlo_result = self._run_monte_carlo_simulation(current_game)
            
            # 4. Actualización bayesiana
            bayesian_probs = self._apply_bayesian_update(pattern_analysis, monte_carlo_result)
            
            # 5. Combinar todas las predicciones
            final_prediction = self._combine_predictions(
                neural_pred, monte_carlo_result, bayesian_probs
            )
            
            # 6. Calcular confianza y nivel de riesgo
            confidence_level, confidence_score = self._calculate_confidence(
                final_prediction, pattern_analysis
            )
            
            # 7. Determinar tamaño de apuesta
            bet_size = self._determine_bet_size(confidence_level, confidence_score)
            
            # 8. Calcular valor esperado
            expected_value = self._calculate_expected_value(final_prediction, bet_size)
            
            # 9. Crear señal
            signal = Signal(
                timestamp=datetime.now(),
                table_id=current_game.table_id,
                confidence=confidence_level,
                recommended_bet=final_prediction['recommended_bet'],
                confidence_score=confidence_score,
                bet_size=bet_size,
                reasoning=final_prediction['reasoning'],
                pattern_analysis=pattern_analysis,
                monte_carlo_probs=monte_carlo_result['probabilities'],
                neural_network_probs=neural_pred['probabilities'],
                expected_value=expected_value,
                risk_level=self._assess_risk_level(confidence_score, expected_value)
            )
            
            # 10. Actualizar estadísticas
            self._update_signal_statistics(signal)
            
            logger.info(f"Señal generada: {signal.recommended_bet} ({confidence_level.value}) - Score: {confidence_score:.3f}")
            return signal
            
        except Exception as e:
            logger.error(f"Error generando señal: {e}")
            return None
    
    def _analyze_current_patterns(self) -> Dict:
        """Analiza patrones en el historial reciente"""
        if len(self.history) < 10:
            return {}
            
        results = [game.result for game in self.history[-50:]]  # Últimas 50 manos
        
        # Análisis de patrones
        streaks = self.pattern_analyzer.detect_streaks(results)
        chops = self.pattern_analyzer.detect_chops(results)
        shoe_patterns = self.pattern_analyzer.analyze_shoe_patterns(results)
        
        return {
            'streaks': streaks,
            'chops': chops,
            'shoe_patterns': shoe_patterns,
            'recent_results': results[-10:],  # Últimas 10
            'pattern_strength': self._calculate_pattern_strength(streaks, chops)
        }
    
    def _get_neural_prediction(self) -> Dict:
        """Obtiene predicción de redes neuronales"""
        if len(self.history) < 20:
            return {'probabilities': {'B': 0.45, 'P': 0.45, 'T': 0.10}}
            
        # Preparar secuencia para LSTM
        recent_results = self.history[-20:]
        sequence = self._prepare_lstm_sequence(recent_results)
        
        # Obtener predicción
        prediction = self.ensemble_predictor.predict_with_confidence(
            lstm_sequence=sequence,
            cnn_results=[game.result for game in self.history[-6:]]
        )
        
        return prediction
    
    def _run_monte_carlo_simulation(self, current_game: GameData) -> Dict:
        """Ejecuta simulación Monte Carlo"""
        current_state = {
            'history': [
                {
                    'result': game.result,
                    'banker_cards': game.banker_cards,
                    'player_cards': game.player_cards
                }
                for game in self.history[-10:]
            ]
        }
        
        return self.monte_carlo.simulate_shoe(current_state, num_hands=10)
    
    def _apply_bayesian_update(self, pattern_analysis: Dict, monte_carlo_result: Dict) -> Dict:
        """Aplica actualización bayesiana"""
        evidence = {
            'streak_length': pattern_analysis.get('streaks', {}).get('current_streak', 0),
            'chop_intensity': pattern_analysis.get('chops', {}).get('chop_intensity', 0),
            'recent_pattern': pattern_analysis.get('recent_results', []),
            'monte_carlo_adjustment': monte_carlo_result.get('probability_adjustments', {})
        }
        
        return self.bayesian.update_probabilities(evidence)
    
    def _combine_predictions(self, neural_pred: Dict, monte_carlo_result: Dict, 
                           bayesian_probs: Dict) -> Dict:
        """Combina todas las predicciones"""
        
        # Pesos para cada método
        weights = {
            'neural': 0.4,
            'monte_carlo': 0.35,
            'bayesian': 0.25
        }
        
        # Combinar probabilidades
        final_probs = {'B': 0, 'P': 0, 'T': 0}
        
        # Neural network probabilities
        if 'probabilities' in neural_pred:
            for outcome, prob in neural_pred['probabilities'].items():
                final_probs[outcome] += prob * weights['neural']
        
        # Monte Carlo probabilities
        mc_probs = monte_carlo_result.get('probability_adjustments', self.base_probabilities)
        for outcome, prob in mc_probs.items():
            final_probs[outcome] += prob * weights['monte_carlo']
        
        # Bayesian probabilities
        for outcome, prob in bayesian_probs.items():
            final_probs[outcome] += prob * weights['bayesian']
        
        # Normalizar
        total = sum(final_probs.values())
        if total > 0:
            final_probs = {k: v/total for k, v in final_probs.items()}
        
        # Determinar apuesta recomendada
        recommended_bet = max(final_probs, key=final_probs.get)
        
        # Razón de la recomendación
        reasoning = {
            'primary_factor': self._determine_primary_factor(final_probs, neural_pred, monte_carlo_result),
            'confidence_sources': self._identify_confidence_sources(neural_pred, monte_carlo_result),
            'pattern_influence': pattern_analysis.get('pattern_strength', 0),
            'statistical_edge': max(final_probs.values()) - 0.5
        }
        
        return {
            'recommended_bet': recommended_bet,
            'probabilities': final_probs,
            'reasoning': reasoning
        }
    
    def _calculate_confidence(self, prediction: Dict, pattern_analysis: Dict) -> Tuple[ConfidenceLevel, float]:
        """Calcula nivel de confianza y score"""
        
        max_prob = max(prediction['probabilities'].values())
        statistical_edge = max_prob - 0.5
        
        # Factores de confianza
        confidence_factors = {
            'statistical_edge': min(1.0, statistical_edge * 4),  # Máxima confianza con 25% edge
            'pattern_strength': pattern_analysis.get('pattern_strength', 0),
            'data_quality': min(1.0, len(self.history) / 100),  # Mejor calidad con más datos
            'model_agreement': self._calculate_model_agreement()
        }
        
        # Score de confianza ponderado
        weights = {'statistical_edge': 0.4, 'pattern_strength': 0.2, 
                  'data_quality': 0.2, 'model_agreement': 0.2}
        
        confidence_score = sum(confidence_factors[k] * weights[k] for k in confidence_factors)
        
        # Determinar nivel de confianza
        if confidence_score >= self.confidence_thresholds['HIGH']:
            confidence_level = ConfidenceLevel.HIGH
        elif confidence_score >= self.confidence_thresholds['MEDIUM']:
            confidence_level = ConfidenceLevel.MEDIUM
        else:
            confidence_level = ConfidenceLevel.LOW
            
        return confidence_level, confidence_score
    
    def _determine_bet_size(self, confidence_level: ConfidenceLevel, confidence_score: float) -> int:
        """Determina tamaño de apuesta basado en confianza"""
        bet_config = self.bet_sizes[confidence_level.value]
        
        if confidence_level == ConfidenceLevel.LOW:
            return 0  # No apostar
        elif confidence_level == ConfidenceLevel.MEDIUM:
            # Escala lineal entre 2-4
            normalized_score = (confidence_score - 0.7) / 0.2  # 0-1
            return int(bet_config['min'] + normalized_score * (bet_config['max'] - bet_config['min']))
        else:  # HIGH
            # Escala lineal entre 5-7
            normalized_score = (confidence_score - 0.9) / 0.08  # 0-1
            return int(bet_config['min'] + normalized_score * (bet_config['max'] - bet_config['min']))
    
    def _calculate_expected_value(self, prediction: Dict, bet_size: int) -> float:
        """Calcula valor esperado de la apuesta"""
        if bet_size == 0:
            return 0.0
            
        recommended_bet = prediction['recommended_bet']
        win_prob = prediction['probabilities'][recommended_bet]
        
        # Pagos típicos
        payouts = {'B': 0.95, 'P': 1.0, 'T': 8.0}
        payout = payouts.get(recommended_bet, 0)
        
        # Valor esperado
        ev = (win_prob * payout * bet_size) - ((1 - win_prob) * bet_size)
        return ev
    
    def _assess_risk_level(self, confidence_score: float, expected_value: float) -> str:
        """Evalúa nivel de riesgo"""
        if confidence_score > 0.85 and expected_value > 0.2:
            return 'LOW'
        elif confidence_score > 0.70 and expected_value > 0.05:
            return 'MEDIUM'
        else:
            return 'HIGH'
    
    @property
    def base_probabilities(self) -> Dict:
        """Probabilidades base de baccarat"""
        return {'B': 0.4584, 'P': 0.4461, 'T': 0.0955}
    
    def _prepare_lstm_sequence(self, games: List[GameData]) -> np.ndarray:
        """Prepara secuencia para LSTM"""
        # Implementación simplificada
        sequence = []
        for game in games:
            feature_vector = [
                1 if game.result == 'B' else 0,
                1 if game.result == 'P' else 0,
                1 if game.result == 'T' else 0,
                game.banker_score / 9.0,
                game.player_score / 9.0,
                game.shoe_position / 80.0
            ]
            sequence.append(feature_vector)
        return np.array(sequence)
    
    def _calculate_pattern_strength(self, streaks: Dict, chops: Dict) -> float:
        """Calcula fuerza del patrón actual"""
        streak_strength = min(1.0, streaks.get('current_streak', 0) / 10)
        chop_strength = chops.get('chop_intensity', 0)
        return max(streak_strength, chop_strength)
    
    def _calculate_model_agreement(self) -> float:
        """Calcula acuerdo entre modelos"""
        # Implementación simplificada - retorna alta confianza
        return 0.8
    
    def _determine_primary_factor(self, final_probs: Dict, neural_pred: Dict, monte_carlo_result: Dict) -> str:
        """Determina el factor principal de la predicción"""
        max_prob = max(final_probs.values())
        if max_prob > 0.7:
            return 'high_probability'
        elif neural_pred.get('confidence') == 'HIGH':
            return 'neural_network'
        elif monte_carlo_result.get('confidence_intervals'):
            return 'monte_carlo'
        else:
            return 'pattern_analysis'
    
    def _identify_confidence_sources(self, neural_pred: Dict, monte_carlo_result: Dict) -> List[str]:
        """Identifica fuentes de confianza"""
        sources = []
        if neural_pred.get('confidence') == 'HIGH':
            sources.append('neural_network')
        if monte_carlo_result.get('probability_adjustments'):
            sources.append('monte_carlo')
        sources.append('pattern_analysis')
        return sources
    
    def _update_signal_statistics(self, signal: Signal):
        """Actualiza estadísticas de señales"""
        self.signal_stats['total_signals'] += 1
        if signal.confidence == ConfidenceLevel.HIGH:
            self.signal_stats['high_confidence_signals'] += 1


class SignalManager:
    """Gestiona el envío y seguimiento de señales"""
    
    def __init__(self, telegram_bot=None):
        self.signal_generator = SignalGenerator()
        self.telegram_bot = telegram_bot
        self.active_signals: List[Signal] = []
        self.signal_history: List[Dict] = []
        
    def process_new_game_data(self, game_data: GameData):
        """Procesa nuevo dato de juego y genera señal si corresponde"""
        
        # Agregar a historial del generador
        self.signal_generator.add_game_data(game_data)
        
        # Generar señal cada 6-8 manos
        if len(self.signal_generator.history) % 7 == 0:  # Cada 7 manos
            signal = self.signal_generator.generate_signal(game_data)
            
            if signal and signal.bet_size > 0:  # Solo señales con apuesta
                self._process_signal(signal)
    
    def _process_signal(self, signal: Signal):
        """Procesa una señal generada"""
        
        # Agregar a señales activas
        self.active_signals.append(signal)
        
        # Limpiar señales antiguas (más de 5 minutos)
        current_time = datetime.now()
        self.active_signals = [
            s for s in self.active_signals 
            if current_time - s.timestamp < timedelta(minutes=5)
        ]
        
        # Enviar notificación
        self._send_signal_notification(signal)
        
        # Agregar a historial
        self.signal_history.append({
            'signal': signal.to_dict(),
            'processed_at': current_time.isoformat()
        })
        
        logger.info(f"Señal procesada: {signal.recommended_bet} ({signal.confidence.value})")
    
    def _send_signal_notification(self, signal: Signal):
        """Envía notificación de señal"""
        
        message = self._format_signal_message(signal)
        
        if self.telegram_bot:
            try:
                self.telegram_bot.send_message(message)
            except Exception as e:
                logger.error(f"Error enviando notificación Telegram: {e}")
        
        # También imprimir en consola
        print(f"\n🎯 SENAL BACCARAT 🎯")
        print(message)
        print("="*50)
    
    def _format_signal_message(self, signal: Signal) -> str:
        """Formatea mensaje de señal para notificación"""
        
        confidence_emoji = {
            'HIGH': '🟢',
            'MEDIUM': '🟡',
            'LOW': '🔴'
        }
        
        bet_emoji = {
            'B': '🏦',
            'P': '👤',
            'T': '🤝'
        }
        
        message = f"""
{confidence_emoji[signal.confidence.value]} CONFIDENCIA: {signal.confidence.value} ({signal.confidence_score:.1%})

💰 APUESTA: {bet_emoji[signal.recommended_bet]} {signal.recommended_bet}
📊 CANTIDAD: {signal.bet_size} unidades
📈 VALOR ESPERADO: {signal.expected_value:+.2f}
⚠️  RIESGO: {signal.risk_level}

🎲 PROBABILIDADES:
   🏦 Banker: {signal.monte_carlo_probs.get('B', 0):.1%}
   👤 Player: {signal.monte_carlo_probs.get('P', 0):.1%}
   🤝 Tie: {signal.monte_carlo_probs.get('T', 0):.1%}

🧠 RAZÓN: {signal.reasoning.get('primary_factor', 'análisis estadístico')}
🕐 TIEMPO: {signal.timestamp.strftime('%H:%M:%S')}
        """
        
        return message.strip()
    
    def get_signal_statistics(self) -> Dict:
        """Obtiene estadísticas de señales"""
        return self.signal_generator.signal_stats.copy()
    
    def get_recent_signals(self, count: int = 10) -> List[Dict]:
        """Obtiene señales recientes"""
        return [s.to_dict() for s in self.active_signals[-count:]]