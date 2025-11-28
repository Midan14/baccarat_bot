"""
Gestión avanzada de riesgos y bankroll
Implementa Kelly Criterion, análisis de volatilidad y protección de capital
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import json
import time
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class RiskLevel(Enum):
    """Niveles de riesgo"""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    EXTREME = "EXTREME"

@dataclass
class BankrollState:
    """Estado actual del bankroll"""
    total_balance: float
    session_balance: float
    daily_balance: float
    weekly_balance: float
    max_drawdown: float
    peak_balance: float
    current_streak: int
    losing_streak: int
    winning_streak: int
    
@dataclass
class BetSizing:
    """Configuración de tamaño de apuesta"""
    base_unit: float
    current_multiplier: float
    max_multiplier: float
    min_multiplier: float
    kelly_fraction: float
    confidence_adjustment: float

class KellyCriterion:
    """Implementación del Kelly Criterion para baccarat"""
    
    def __init__(self, conservative_factor: float = 0.25):
        self.conservative_factor = conservative_factor  # Usar solo 25% del Kelly óptimo
        
    def calculate_kelly_fraction(self, win_probability: float, odds: float) -> float:
        """Calcula fracción óptima de Kelly"""
        if win_probability <= 0 or win_probability >= 1:
            return 0.0
            
        # Fórmula Kelly: f* = (bp - q) / b
        # b = odds - 1 (decimal odds)
        # p = probabilidad de ganar
        # q = probabilidad de perder
        
        b = odds - 1
        p = win_probability
        q = 1 - p
        
        kelly_fraction = (b * p - q) / b
        
        # Aplicar factor conservador
        return max(0.0, kelly_fraction * self.conservative_factor)
    
    def calculate_bet_size(self, bankroll: float, kelly_fraction: float, 
                          max_bet_pct: float = 0.05) -> float:
        """Calcula tamaño de apuesta basado en Kelly"""
        optimal_bet = bankroll * kelly_fraction
        max_bet = bankroll * max_bet_pct
        
        return min(optimal_bet, max_bet)

class VolatilityAnalyzer:
    """Analiza volatilidad de sesiones y ajusta estrategias"""
    
    def __init__(self, window_size: int = 50):
        self.window_size = window_size
        self.results_history: List[float] = []
        
    def add_result(self, result: float):
        """Agrega resultado (ganancia/pérdida)"""
        self.results_history.append(result)
        
        # Mantener tamaño de ventana
        if len(self.results_history) > self.window_size:
            self.results_history.pop(0)
    
    def calculate_volatility(self) -> float:
        """Calcula volatilidad actual"""
        if len(self.results_history) < 10:
            return 0.1  # Volatilidad por defecto
            
        returns = np.array(self.results_history)
        return np.std(returns)
    
    def get_volatility_adjustment(self) -> float:
        """Obtiene ajuste basado en volatilidad"""
        volatility = self.calculate_volatility()
        
        # Ajustar multiplicador de apuesta basado en volatilidad
        if volatility < 0.5:
            return 1.2  # Aumentar en baja volatilidad
        elif volatility < 1.0:
            return 1.0  # Normal
        elif volatility < 2.0:
            return 0.8  # Reducir en alta volatilidad
        else:
            return 0.6  # Reducir significativamente en volatilidad extrema
    
    def predict_session_volatility(self) -> RiskLevel:
        """Predice volatilidad de la sesión"""
        volatility = self.calculate_volatility()
        
        if volatility < 0.5:
            return RiskLevel.LOW
        elif volatility < 1.0:
            return RiskLevel.MEDIUM
        elif volatility < 2.0:
            return RiskLevel.HIGH
        else:
            return RiskLevel.EXTREME

class RiskManager:
    """Gestor principal de riesgos"""
    
    def __init__(self, initial_bankroll: float, base_unit: float = 10.0):
        self.initial_bankroll = initial_bankroll
        self.current_bankroll = initial_bankroll
        self.base_unit = base_unit
        
        # Componentes
        self.kelly = KellyCriterion()
        self.volatility_analyzer = VolatilityAnalyzer()
        
        # Límites y umbrales
        self.limits = {
            'max_daily_loss': initial_bankroll * 0.1,      # 10% máximo pérdida diaria
            'max_session_loss': initial_bankroll * 0.05,   # 5% máximo pérdida por sesión
            'max_drawdown': initial_bankroll * 0.2,        # 20% máximo drawdown
            'daily_profit_target': initial_bankroll * 0.05, # 5% objetivo diario
            'session_profit_target': initial_bankroll * 0.02 # 2% objetivo por sesión
        }
        
        # Estado del bankroll
        self.bankroll_state = BankrollState(
            total_balance=initial_bankroll,
            session_balance=initial_bankroll,
            daily_balance=initial_bankroll,
            weekly_balance=initial_bankroll,
            max_drawdown=0,
            peak_balance=initial_bankroll,
            current_streak=0,
            losing_streak=0,
            winning_streak=0
        )
        
        # Seguimiento de sesión
        self.session_start_time = datetime.now()
        self.daily_start_time = datetime.now()
        self.session_results: List[float] = []
        self.daily_results: List[float] = []
        
        # Flags de control
        self.session_active = False
        self.emergency_stop = False
        self.cooling_down = False
        
    def start_session(self):
        """Inicia nueva sesión"""
        self.session_active = True
        self.session_start_time = datetime.now()
        self.session_results = []
        self.bankroll_state.session_balance = self.current_bankroll
        
        logger.info(f"Sesión iniciada. Bankroll: ${self.current_bankroll:.2f}")
    
    def end_session(self):
        """Finaliza sesión actual"""
        self.session_active = False
        session_profit = sum(self.session_results)
        
        logger.info(f"Sesión finalizada. Resultado: ${session_profit:+.2f}")
        
        # Actualizar estadísticas
        self._update_session_statistics()
    
    def should_continue_session(self) -> bool:
        """Determina si se debe continuar la sesión"""
        
        if not self.session_active:
            return False
            
        if self.emergency_stop:
            logger.warning("Parada de emergencia activada")
            return False
            
        # Verificar límites de pérdida
        session_loss = self.bankroll_state.session_balance - self.current_bankroll
        if session_loss >= self.limits['max_session_loss']:
            logger.warning(f"Límite de pérdida de sesión alcanzado: ${session_loss:.2f}")
            return False
            
        # Verificar límites de ganancia
        session_profit = self.current_bankroll - self.bankroll_state.session_balance
        if session_profit >= self.limits['session_profit_target']:
            logger.info(f"Objetivo de ganancia de sesión alcanzado: ${session_profit:.2f}")
            return False
            
        # Verificar tiempo máximo de sesión (2 horas)
        session_duration = datetime.now() - self.session_start_time
        if session_duration.total_seconds() > 7200:  # 2 horas
            logger.info("Tiempo máximo de sesión alcanzado")
            return False
            
        # Verificar volatilidad extrema
        current_volatility = self.volatility_analyzer.calculate_volatility()
        if current_volatility > 3.0:
            logger.warning("Volatilidad extrema detectada, deteniendo sesión")
            return False
            
        return True
    
    def calculate_bet_size(self, win_probability: float, confidence_level: str, 
                          odds: float = 1.0) -> float:
        """Calcula tamaño óptimo de apuesta"""
        
        if self.emergency_stop or not self.session_active:
            return 0.0
            
        # Calcular fracción Kelly
        kelly_fraction = self.kelly.calculate_kelly_fraction(win_probability, odds)
        
        # Calcular apuesta base Kelly
        kelly_bet = self.kelly.calculate_bet_size(self.current_bankroll, kelly_fraction)
        
        # Ajustar por nivel de confianza
        confidence_multiplier = {
            'HIGH': 1.0,
            'MEDIUM': 0.7,
            'LOW': 0.4
        }.get(confidence_level, 0.5)
        
        # Ajustar por volatilidad
        volatility_multiplier = self.volatility_analyzer.get_volatility_adjustment()
        
        # Calcular apuesta final
        final_bet = kelly_bet * confidence_multiplier * volatility_multiplier
        
        # Asegurar que no exceda límites
        max_bet = self.current_bankroll * 0.05  # Máximo 5% del bankroll
        min_bet = self.base_unit  # Mínimo 1 unidad base
        
        final_bet = max(min_bet, min(final_bet, max_bet))
        
        return final_bet
    
    def record_bet_result(self, bet_amount: float, result: float, outcome: str):
        """Registra resultado de apuesta"""
        
        # Actualizar bankroll
        self.current_bankroll += result
        
        # Agregar a historiales
        self.session_results.append(result)
        self.daily_results.append(result)
        self.volatility_analyzer.add_result(result)
        
        # Actualizar estadísticas de rachas
        if result > 0:
            self.bankroll_state.winning_streak += 1
            self.bankroll_state.losing_streak = 0
            self.bankroll_state.current_streak += 1
        else:
            self.bankroll_state.losing_streak += 1
            self.bankroll_state.winning_streak = 0
            self.bankroll_state.current_streak -= 1
            
        # Actualizar peak balance y drawdown
        if self.current_bankroll > self.bankroll_state.peak_balance:
            self.bankroll_state.peak_balance = self.current_bankroll
            
        current_drawdown = (self.bankroll_state.peak_balance - self.current_bankroll) / self.bankroll_state.peak_balance
        if current_drawdown > self.bankroll_state.max_drawdown:
            self.bankroll_state.max_drawdown = current_drawdown
            
        # Verificar drawdown máximo
        if self.bankroll_state.max_drawdown > 0.15:  # 15% drawdown
            logger.warning(f"Drawdown elevado: {self.bankroll_state.max_drawdown:.1%}")
            
        # Verificar parada de emergencia
        if self.bankroll_state.max_drawdown > 0.20:  # 20% drawdown
            self.emergency_stop = True
            logger.critical("Drawdown máximo alcanzado - Parada de emergencia")
            
        logger.info(f"Resultado: ${result:+.2f} | Bankroll: ${self.current_bankroll:.2f}")
    
    def get_risk_assessment(self) -> Dict:
        """Obtiene evaluación completa de riesgo"""
        
        current_volatility = self.volatility_analyzer.calculate_volatility()
        volatility_risk = self.volatility_analyzer.predict_session_volatility()
        
        # Calcular VAR (Value at Risk) a 95%
        if len(self.session_results) > 10:
            var_95 = np.percentile(self.session_results, 5)
        else:
            var_95 = -self.base_unit * 5  # Estimación conservadora
            
        return {
            'current_bankroll': self.current_bankroll,
            'session_profit_loss': sum(self.session_results),
            'daily_profit_loss': sum(self.daily_results),
            'max_drawdown': self.bankroll_state.max_drawdown,
            'current_volatility': current_volatility,
            'volatility_risk': volatility_risk.value,
            'value_at_risk_95': var_95,
            'current_streak': self.bankroll_state.current_streak,
            'losing_streak': self.bankroll_state.losing_streak,
            'winning_streak': self.bankroll_state.winning_streak,
            'emergency_stop_active': self.emergency_stop,
            'session_active': self.session_active
        }
    
    def get_bet_sizing_recommendation(self, win_probability: float, 
                                    confidence_level: str) -> Dict:
        """Obtiene recomendación completa de tamaño de apuesta"""
        
        bet_size = self.calculate_bet_size(win_probability, confidence_level)
        risk_assessment = self.get_risk_assessment()
        
        # Calcular riesgo de la apuesta
        bet_risk = self._assess_bet_risk(bet_size, win_probability)
        
        # Ajustes adicionales
        adjustments = {
            'volatility_adjustment': self.volatility_analyzer.get_volatility_adjustment(),
            'streak_adjustment': self._get_streak_adjustment(),
            'time_adjustment': self._get_time_adjustment()
        }
        
        return {
            'recommended_bet_size': bet_size,
            'base_unit': self.base_unit,
            'kelly_fraction': self.kelly.calculate_kelly_fraction(win_probability, 1.0),
            'risk_assessment': risk_assessment,
            'bet_risk_level': bet_risk,
            'adjustments': adjustments,
            'justification': self._get_bet_sizing_justification(bet_size, adjustments)
        }
    
    def _update_session_statistics(self):
        """Actualiza estadísticas de la sesión"""
        session_profit = sum(self.session_results)
        self.bankroll_state.session_balance = self.current_bankroll
        
        # Actualizar balance diario
        if datetime.now().date() != self.daily_start_time.date():
            self.daily_results = []
            self.daily_start_time = datetime.now()
            
    def _assess_bet_risk(self, bet_size: float, win_probability: float) -> RiskLevel:
        """Evalúa riesgo de una apuesta específica"""
        bet_percentage = bet_size / self.current_bankroll
        
        if bet_percentage > 0.05 or win_probability < 0.5:
            return RiskLevel.HIGH
        elif bet_percentage > 0.03 or win_probability < 0.6:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW
    
    def _get_streak_adjustment(self) -> float:
        """Obtiene ajuste basado en rachas"""
        if self.bankroll_state.losing_streak > 5:
            return 0.5  # Reducir en racha perdedora
        elif self.bankroll_state.winning_streak > 5:
            return 1.1  # Aumentar levemente en racha ganadora
        else:
            return 1.0
    
    def _get_time_adjustment(self) -> float:
        """Obtiene ajuste basado en tiempo de sesión"""
        session_duration = datetime.now() - self.session_start_time
        hours = session_duration.total_seconds() / 3600
        
        if hours > 1.5:
            return 0.8  # Reducir en sesiones largas
        else:
            return 1.0
    
    def _get_bet_sizing_justification(self, bet_size: float, adjustments: Dict) -> str:
        """Obtiene justificación para el tamaño de apuesta"""
        factors = []
        
        if adjustments['volatility_adjustment'] != 1.0:
            factors.append("volatilidad")
        if adjustments['streak_adjustment'] != 1.0:
            factors.append("racha")
        if adjustments['time_adjustment'] != 1.0:
            factors.append("tiempo de sesión")
            
        if factors:
            return f"Ajustado por: {', '.join(factors)}"
        else:
            return "Tamaño óptimo según Kelly Criterion"


class StopLossManager:
    """Gestiona stop-loss dinámicos"""
    
    def __init__(self):
        self.stop_loss_levels = {
            'tight': 0.02,    # 2% stop-loss
            'medium': 0.05,   # 5% stop-loss
            'loose': 0.08     # 8% stop-loss
        }
        
        self.current_stop_loss = 0.05  # Stop-loss por defecto
        self.trailing_stop = None
        
    def update_stop_loss(self, current_balance: float, peak_balance: float, 
                        volatility: float) -> float:
        """Actualiza nivel de stop-loss basado en condiciones"""
        
        # Ajustar por volatilidad
        if volatility < 0.5:
            self.current_stop_loss = self.stop_loss_levels['tight']
        elif volatility < 1.0:
            self.current_stop_loss = self.stop_loss_levels['medium']
        else:
            self.current_stop_loss = self.stop_loss_levels['loose']
            
        # Trailing stop
        if self.trailing_stop is None or current_balance > self.trailing_stop:
            self.trailing_stop = current_balance * (1 - self.current_stop_loss)
            
        return self.trailing_stop
    
    def should_stop(self, current_balance: float, initial_balance: float) -> bool:
        """Determina si se debe detener"""
        # Stop-loss fijo
        if current_balance <= initial_balance * (1 - self.current_stop_loss):
            return True
            
        # Trailing stop
        if self.trailing_stop and current_balance <= self.trailing_stop:
            return True
            
        return False