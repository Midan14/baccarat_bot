# core/kelly_bankroll_manager.py
import numpy as np
from typing import Tuple, Dict
from config.settings import settings

class KellyBankrollManager:
    """Gestor de bankroll basado en Kelly Criterion óptimo"""
    
    def __init__(self, initial_bankroll: float):
        self.initial_bankroll = initial_bankroll
        self.current_bankroll = initial_bankroll
        self.fractional_kelly = 0.25  # Conservador: usar 1/4 Kelly
        self.bet_history = []
        self.true_outcome_probs = {'Dragon': 0.446, 'Tiger': 0.446, 'Tie': 0.108}
        
        # Mapping de payouts
        self.payouts = {'Dragon': 1.0, 'Tiger': 1.0, 'Tie': 11.0}
    
    def calculate_kelly_bet(self, perceived_prob: float, bet_type: str, edge_threshold: float = 0.02) -> Tuple[float, bool, str]:
        """
        Calcular tamaño de apuesta óptimo usando Kelly Criterion
        Returns: (tamaño_apuesta, deber_apostar, razón)
        """
        payout = self.payouts[bet_type]
        true_prob = self.true_outcome_probs[bet_type]
        
        # Edge = ventaja percibida
        edge = (perceived_prob * payout) - 1
        
        # Solo apostar si hay edge significativo
        if edge < edge_threshold:
            return 0.0, False, f"Edge insuficiente: {edge:.3f} < {edge_threshold}"
        
        # Kelly Criterion: f* = (bp - q) / b
        # donde b = payout, p = probabilidad de ganar, q = 1-p
        b = payout - 1  # odds
        p = perceived_prob
        q = 1 - p
        
        kelly_fraction = (b * p - q) / b
        
        # Kelly fraccional conservador
        bet_size = self.current_bankroll * kelly_fraction * self.fractional_kelly
        
        # Limitar a rangos configurados
        bet_size = max(settings.bankroll.min_bet, min(bet_size, settings.bankroll.max_bet))
        
        # Verificar bankroll suficiente
        if bet_size > self.current_bankroll * 0.1:  # No arriesgar >10% en una apuesta
            bet_size = self.current_bankroll * 0.1
        
        return bet_size, True, f"Edge: {edge:.3f}, Kelly frac: {kelly_fraction:.3f}"
    
    def update_bankroll(self, bet_size: float, outcome: str, predicted: str, actual_payout: float):
        """Actualizar bankroll y registrar métricas"""
        if outcome == predicted:
            profit = actual_payout - bet_size
        else:
            profit = -bet_size
        
        self.current_bankroll += profit
        self.bet_history.append({
            'bet_size': bet_size,
            'predicted': predicted,
            'outcome': outcome,
            'profit': profit,
            'bankroll': self.current_bankroll
        })
        
        # Ajustar Kelly fraccional basado en drawdown
        max_bankroll = max([self.initial_bankroll] + [b['bankroll'] for b in self.bet_history])
        drawdown = (max_bankroll - self.current_bankroll) / max_bankroll
        
        # Reducir exposición en drawdowns
        if drawdown > 0.2:
            self.fractional_kelly = 0.1  # Muy conservador
        elif drawdown > 0.1:
            self.fractional_kelly = 0.2
        else:
            self.fractional_kelly = 0.25  # Normal
    
    def get_performance_metrics(self) -> Dict[str, float]:
        """Calcular métricas de rendimiento avanzadas"""
        if not self.bet_history:
            return {}
        
        profits = [b['profit'] for b in self.bet_history]
        bet_sizes = [b['bet_size'] for b in self.bet_history]
        
        total_return = self.current_bankroll / self.initial_bankroll - 1
        volatility = np.std(profits) / np.mean(bet_sizes) if np.mean(bet_sizes) > 0 else 0
        
        # Sharpe ratio (asumiendo risk-free rate = 0)
        sharpe = np.mean(profits) / np.std(profits) if np.std(profits) > 0 else 0
        
        # Sortino ratio (solo downside deviation)
        downside = [p for p in profits if p < 0]
        downside_dev = np.std(downside) if downside else 0.01
        sortino = np.mean(profits) / downside_dev
        
        # Max drawdown
        cumulative = np.cumsum(profits)
        running_max = np.maximum.accumulate(np.concatenate([[0], cumulative]))
        drawdowns = cumulative - running_max[:-1]
        max_drawdown = abs(np.min(drawdowns)) / self.initial_bankroll
        
        return {
            'roi': total_return * 100,
            'volatility': volatility,
            'sharpe_ratio': sharpe,
            'sortino_ratio': sortino,
            'max_drawdown_pct': max_drawdown * 100,
            'current_bankroll': self.current_bankroll,
            'total_bets': len(self.bet_history)
        }