# core/decision_engine.py
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass
from config.settings import settings
from utils.logger import logger
from core.prediction_engine import PredictionResult

@dataclass
class BettingDecision:
    """Decisión final de apuesta"""
    should_bet: bool
    bet_type: str  # 'B', 'P', 'E'
    amount: float
    confidence: float
    signal_source: str
    reason: str

class DecisionEngine:
    """Motor de decisión con gestión de bankroll"""
    
    def __init__(self):
        self.current_bankroll = 1000.0  # Bankroll inicial
        self.consecutive_losses = 0
        self.total_bets = 0
        self.wins = 0
        self.current_streak = 0
        self.last_bet_amount = 0.0
        
        # Estadísticas
        self.stats = {
            'total_bets': 0,
            'wins': 0,
            'losses': 0,
            'profit': 0.0,
            'win_streak': 0,
            'loss_streak': 0
        }
    
    def make_decision(self, prediction: PredictionResult, game_state: Dict[str, Any]) -> BettingDecision:
        """Tomar decisión final de apuesta"""
        
        # Verificar condiciones básicas
        if not self._should_consider_bet(prediction, game_state):
            return BettingDecision(False, '', 0.0, 0.0, '', "Condiciones no cumplidas")
        
        # Calcular monto de apuesta
        bet_amount = self._calculate_bet_amount(prediction.confidence)
        
        # Verificar límites de bankroll
        if not self._validate_bet_amount(bet_amount):
            return BettingDecision(False, '', 0.0, 0.0, '', f"Bankroll insuficiente: {bet_amount}")
        
        # Decisión final
        return BettingDecision(
            should_bet=True,
            bet_type=prediction.signal,
            amount=bet_amount,
            confidence=prediction.confidence,
            signal_source=prediction.algorithm,
            reason=f"Señal {prediction.signal} con {prediction.confidence:.2f} de confianza"
        )
    
    def _should_consider_bet(self, prediction: PredictionResult, game_state: Dict[str, Any]) -> bool:
        """Determinar si se debe considerar una apuesta"""
        
        # Verificar señal válida
        if prediction.signal == 'NONE' or prediction.confidence < 0.4:
            return False
        
        # Verificar datos suficientes
        history = game_state.get('history', [])
        if len(history) < settings.prediction.min_data_points:
            return False
        
        # Verificar si la apuesta está abierta
        if not game_state.get('betting_open', True):
            return False
        
        # Verificar stop loss/win
        if self.stats['profit'] <= -settings.bankroll.stop_loss:
            logger.warning(f"STOP LOSS alcanzado: {self.stats['profit']}")
            return False
        
        if self.stats['profit'] >= settings.bankroll.stop_win:
            logger.warning(f"STOP WIN alcanzado: {self.stats['profit']}")
            return False
        
        return True
    
    def _calculate_bet_amount(self, confidence: float) -> float:
        # Estrategia de apuesta basada en confianza
        if confidence < 0.5:
            return 0.0
        
        # Apuesta proporcional a la confianza
        base_bet = settings.bankroll.base_bet
        bet_amount = base_bet * confidence
        
        # Aplicar límites
        return min(bet_amount, settings.bankroll.max_bet)
    
    def _martingale_strategy(self, confidence: float) -> float:
        """Estrategia Martingala (peligrosa)"""
        if self.consecutive_losses == 0:
            bet_amount = settings.bankroll.base_bet
        else:
            bet_amount = settings.bankroll.base_bet * (2 ** self.consecutive_losses)
        
        # Aplicar factor de confianza
        bet_amount *= confidence
        
        return min(bet_amount, settings.bankroll.max_bet)
    
    def _fibonacci_strategy(self, confidence: float) -> float:
        """Estrategia Fibonacci"""
        fibonacci = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55]
        
        if self.consecutive_losses >= len(fibonacci):
            level = len(fibonacci) - 1
        else:
            level = self.consecutive_losses
        
        bet_amount = settings.bankroll.base_bet * fibonacci[level] * confidence
        return min(bet_amount, settings.bankroll.max_bet)
    
    def _flat_strategy(self, confidence: float) -> float:
        """Estrategia de apuesta plana"""
        return settings.bankroll.base_bet * confidence
    
    def _validate_bet_amount(self, amount: float) -> bool:
        """Validar que el monto de apuesta sea viable"""
        return amount <= self.current_bankroll and amount <= settings.bankroll.max_bet
    
    def record_result(self, bet_decision: BettingDecision, won: bool, payout: float = 0.0):
        """Registrar resultado de la apuesta"""
        self.total_bets += 1
        self.last_bet_amount = bet_decision.amount
        
        if won:
            self.wins += 1
            self.consecutive_losses = 0
            self.current_streak = max(self.current_streak, 0) + 1
            profit = payout - bet_decision.amount
            self.stats['win_streak'] = max(self.stats['win_streak'], self.current_streak)
        else:
            self.consecutive_losses += 1
            self.current_streak = min(self.current_streak, 0) - 1
            profit = -bet_decision.amount
            self.stats['loss_streak'] = min(self.stats['loss_streak'], self.current_streak)
        
        self.current_bankroll += profit
        self.stats['profit'] += profit
        self.stats['total_bets'] = self.total_bets
        self.stats['wins'] = self.wins
        self.stats['losses'] = self.total_bets - self.wins
        
        logger.info(f"Resultado: {'GANADA' if won else 'PERDIDA'} | "
                   f"Bankroll: {self.current_bankroll:.2f} | "
                   f"Profit Total: {self.stats['profit']:.2f}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas actuales"""
        win_rate = (self.wins / self.total_bets * 100) if self.total_bets > 0 else 0
        return {
            **self.stats,
            'win_rate': win_rate,
            'current_bankroll': self.current_bankroll,
            'consecutive_losses': self.consecutive_losses,
            'current_streak': self.current_streak
        }