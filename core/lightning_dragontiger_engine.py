# core/lightning_dragontiger_engine.py
"""
Motor de análisis y predicción específico para Lightning Dragon Tiger
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from utils.logger import logger

@dataclass
class DragonTigerPrediction:
    """Predicción para Lightning Dragon Tiger"""
    signal: str  # Dragon, Tiger, Tie
    confidence: float
    reasoning: str
    recommended_bet: str
    lightning_multiplier: Optional[int] = None
    expected_value: float = 0.0

@dataclass
class GameState:
    """Estado del juego Lightning Dragon Tiger"""
    history: List[str]  # Dragon, Tiger, Tie
    dragon_cards: List[str]
    tiger_cards: List[str]
    lightning_multipliers: Dict[str, List[int]]
    current_round: int
    betting_open: bool

class LightningDragonTigerEngine:
    """Motor de análisis para Lightning Dragon Tiger"""
    
    def __init__(self):
        self.name = "Lightning Dragon Tiger Engine"
        self.game_type = "lightning_dragontiger"
        
    def analyze(self, game_state: GameState) -> DragonTigerPrediction:
        """
        Analizar el estado del juego y generar predicción
        """
        logger.info("Analizando estado del juego Lightning Dragon Tiger...")
        
        # 1. Análisis de tendencias
        trend_signal = self._analyze_trends(game_state.history)
        
        # 2. Análisis de frecuencias
        freq_signal = self._analyze_frequencies(game_state.history)
        
        # 3. Análisis de patrones
        pattern_signal = self._analyze_patterns(game_state.history)
        
        # 4. Análisis de Lightning multiplicadores
        lightning_analysis = self._analyze_lightning_multipliers(game_state.lightning_multipliers)
        
        # 5. Combinar análisis
        final_prediction = self._combine_analyses(
            trend_signal, freq_signal, pattern_signal, lightning_analysis
        )
        
        logger.info(f"Predicción generada: {final_prediction.signal} "
                   f"(confianza: {final_prediction.confidence:.2f})")
        
        return final_prediction
    
    def _analyze_trends(self, history: List[str]) -> Dict[str, float]:
        """Analizar tendencias en el historial"""
        if len(history) < 3:
            return {"Dragon": 0.33, "Tiger": 0.33, "Tie": 0.34}
        
        # Últimas 10 rondas
        recent = history[-10:] if len(history) >= 10 else history
        
        # Contar streaks
        dragon_streak = 0
        tiger_streak = 0
        tie_streak = 0
        
        current_streak = 1
        for i in range(1, len(recent)):
            if recent[i] == recent[i-1]:
                current_streak += 1
            else:
                if recent[i-1] == "Dragon":
                    dragon_streak = max(dragon_streak, current_streak)
                elif recent[i-1] == "Tiger":
                    tiger_streak = max(tiger_streak, current_streak)
                elif recent[i-1] == "Tie":
                    tie_streak = max(tie_streak, current_streak)
                current_streak = 1
        
        # Análisis de anti-tendencia
        if len(history) >= 2:
            last_two = history[-2:]
            if last_two[0] == last_two[1]:
                # Misma salida dos veces, probabilidad de cambio aumenta
                anti_trend_factor = 0.15
                if last_two[0] == "Dragon":
                    return {"Dragon": 0.25, "Tiger": 0.45, "Tie": 0.30}
                elif last_two[0] == "Tiger":
                    return {"Dragon": 0.45, "Tiger": 0.25, "Tie": 0.30}
        
        # Distribución basada en frecuencia reciente
        dragon_count = recent.count("Dragon")
        tiger_count = recent.count("Tiger")
        tie_count = recent.count("Tie")
        
        total = len(recent)
        return {
            "Dragon": dragon_count / total,
            "Tiger": tiger_count / total,
            "Tie": tie_count / total
        }
    
    def _analyze_frequencies(self, history: List[str]) -> Dict[str, float]:
        """Analizar frecuencias de aparición"""
        if not history:
            return {"Dragon": 0.446, "Tiger": 0.446, "Tie": 0.108}
        
        # Ventana de análisis
        window_size = min(50, len(history))
        window = history[-window_size:]
        
        # Contar frecuencias
        dragon_freq = window.count("Dragon") / window_size
        tiger_freq = window.count("Tiger") / window_size
        tie_freq = window.count("Tie") / window_size
        
        # Ajustar según probabilidades teóricas
        theoretical = {"Dragon": 0.446, "Tiger": 0.446, "Tie": 0.108}
        
        # Si hay desviación significativa, ajustar
        adjusted = {}
        for outcome in ["Dragon", "Tiger", "Tie"]:
            observed = {"Dragon": dragon_freq, "Tiger": tiger_freq, "Tie": tie_freq}[outcome]
            theoretical_prob = theoretical[outcome]
            
            # Si la observada es significativamente diferente, ajustar
            if abs(observed - theoretical_prob) > 0.05:
                adjusted[outcome] = observed
            else:
                adjusted[outcome] = theoretical_prob
        
        return adjusted
    
    def _analyze_patterns(self, history: List[str]) -> Dict[str, float]:
        """Analizar patrones en el historial"""
        if len(history) < 4:
            return {"Dragon": 0.33, "Tiger": 0.33, "Tie": 0.34}
        
        # Buscar patrones comunes en Dragon Tiger
        patterns = {
            "alternating": 0,
            "streaks": 0,
            "pairs": 0,
            "random": 0
        }
        
        # Analizar últimas 20 rondas
        sample_size = min(20, len(history))
        sample = history[-sample_size:]
        
        for i in range(2, len(sample)):
            # Patrón alternante (D-T-D-T o T-D-T-D)
            if (sample[i] != sample[i-1] and 
                sample[i-1] != sample[i-2] and 
                sample[i] == sample[i-2]):
                patterns["alternating"] += 1
            
            # Patrón de streaks (mismo resultado 3+ veces)
            if sample[i] == sample[i-1] == sample[i-2]:
                patterns["streaks"] += 1
            
            # Patrón de pares (dos iguales, cambio, dos iguales)
            if i >= 4 and sample[i-3:i-1].count(sample[i-3]) == 2 and sample[i-1] != sample[i-3]:
                patterns["pairs"] += 1
        
        # Determinar patrón dominante
        total_patterns = sum(patterns.values())
        if total_patterns > 0:
            dominant_pattern = max(patterns, key=patterns.get)
            
            # Ajustar predicción según patrón dominante
            if dominant_pattern == "alternating":
                # Si alterna, predecir alternancia
                last = history[-1]
                if last == "Dragon":
                    return {"Dragon": 0.20, "Tiger": 0.70, "Tie": 0.10}
                else:
                    return {"Dragon": 0.70, "Tiger": 0.20, "Tie": 0.10}
            elif dominant_pattern == "streaks":
                # Si hay streaks, predecir continuación
                last = history[-1]
                return {last: 0.60, "Dragon": 0.20, "Tiger": 0.20, "Tie": 0.10}
        
        # Si no hay patrón claro, distribución equilibrada
        return {"Dragon": 0.40, "Tiger": 0.40, "Tie": 0.20}
    
    def _analyze_lightning_multipliers(self, multipliers: Dict[str, List[int]]) -> Dict[str, float]:
        """Analizar multiplicadores Lightning"""
        if not multipliers:
            return {"Dragon": 0.33, "Tiger": 0.33, "Tie": 0.34}
        
        # Calcular valor esperado de cada apuesta con multiplicadores
        ev_scores = {}
        
        for bet_type in ["Dragon", "Tiger", "Tie"]:
            if bet_type in multipliers and multipliers[bet_type]:
                avg_multiplier = sum(multipliers[bet_type]) / len(multipliers[bet_type])
                
                # Valor esperado = (probabilidad de ganar * (multiplicador * payout)) - probabilidad de perder
                if bet_type == "Tie":
                    prob_win = 0.108  # Probabilidad teórica de Tie
                    base_payout = 11.0
                else:
                    prob_win = 0.446  # Probabilidad teórica de Dragon/Tiger
                    base_payout = 1.0
                
                ev = (prob_win * avg_multiplier * base_payout) - (1 - prob_win)
                ev_scores[bet_type] = max(ev, 0)  # No negativo
            else:
                ev_scores[bet_type] = 0.33  # Valor por defecto
        
        # Normalizar
        total = sum(ev_scores.values())
        if total > 0:
            return {k: v/total for k, v in ev_scores.items()}
        
        return {"Dragon": 0.33, "Tiger": 0.33, "Tie": 0.34}
    
    def _combine_analyses(self, trend: Dict[str, float], 
                         freq: Dict[str, float], 
                         pattern: Dict[str, float],
                         lightning: Dict[str, float]) -> DragonTigerPrediction:
        """Combinar todos los análisis en una predicción final"""
        
        # Pesos para cada tipo de análisis
        weights = {
            "trend": 0.25,
            "frequency": 0.25,
            "pattern": 0.25,
            "lightning": 0.25
        }
        
        # Combinar predicciones
        combined = {"Dragon": 0, "Tiger": 0, "Tie": 0}
        
        for outcome in ["Dragon", "Tiger", "Tie"]:
            combined[outcome] = (
                weights["trend"] * trend.get(outcome, 0.33) +
                weights["frequency"] * freq.get(outcome, 0.33) +
                weights["pattern"] * pattern.get(outcome, 0.33) +
                weights["lightning"] * lightning.get(outcome, 0.34)
            )
        
        # Normalizar
        total = sum(combined.values())
        if total > 0:
            combined = {k: v/total for k, v in combined.items()}
        
        # Seleccionar la predicción con mayor probabilidad
        best_prediction = max(combined, key=combined.get)
        confidence = combined[best_prediction]
        
        # Determinar si hay multiplicador Lightning recomendado
        lightning_multiplier = None
        if best_prediction in lightning and lightning[best_prediction] > 0.4:
            # Si Lightning favorece esta apuesta, sugerir multiplicador
            lightning_multiplier = 5  # Valor moderado por defecto
        
        # Calcular valor esperado
        expected_value = self._calculate_expected_value(best_prediction, combined)
        
        return DragonTigerPrediction(
            signal=best_prediction,
            confidence=confidence,
            reasoning=f"Análisis combinado: tendencia {weights['trend']:.0%}, "
                     f"frecuencia {weights['frequency']:.0%}, patrón {weights['pattern']:.0%}, "
                     f"lightning {weights['lightning']:.0%}",
            recommended_bet=best_prediction,
            lightning_multiplier=lightning_multiplier,
            expected_value=expected_value
        )
    
    def _calculate_expected_value(self, prediction: str, probabilities: Dict[str, float]) -> float:
        """Calcular el valor esperado de la predicción"""
        # Valores base según el tipo de apuesta
        base_values = {"Dragon": 1.0, "Tiger": 1.0, "Tie": 11.0}
        
        # Probabilidades teóricas
        theoretical_probs = {"Dragon": 0.446, "Tiger": 0.446, "Tie": 0.108}
        
        # Calcular EV
        prob = probabilities.get(prediction, theoretical_probs[prediction])
        payout = base_values[prediction]
        
        ev = (prob * payout) - (1 - prob)
        return ev