# core/backtester.py
import pandas as pd
import numpy as np
from typing import List, Dict, Callable
from dataclasses import dataclass
import matplotlib.pyplot as plt
from tqdm import tqdm

@dataclass
class BacktestResult:
    """Resultados de backtesting"""
    total_return: float
    sharpe_ratio: float
    max_drawdown: float
    win_rate: float
    profit_factor: float
    total_trades: int
    equity_curve: np.ndarray
    detailed_stats: Dict

class BaccaratBacktester:
    """Framework de backtesting robusto"""
    
    def __init__(self, historical_data: List[str], initial_bankroll: float = 1000):
        self.data = historical_data
        self.initial_bankroll = initial_bankroll
    
    def run_backtest(self, 
                     strategy_func: Callable,
                     prediction_engine,
                     min_history: int = 60) -> BacktestResult:
        """
        Ejecutar backtesting de una estrategia completa
        """
        bankroll = self.initial_bankroll
        bankroll_history = [bankroll]
        trades = []
        
        # Iterar con barra de progreso
        for i in tqdm(range(min_history, len(self.data) - 1), desc="Backtesting"):
            history_window = self.data[:i]
            actual_next = self.data[i]
            
            # Obtener predicción
            try:
                prediction = prediction_engine.analyze(history_window)
            except:
                continue
                
            if prediction.signal == 'NONE':
                bankroll_history.append(bankroll)
                continue
            
            # Ejecutar estrategia
            decision = strategy_func(prediction, {'history': history_window})
            
            if not decision.should_bet:
                bankroll_history.append(bankroll)
                continue
            
            # Simular resultado
            won = decision.bet_type == actual_next
            payout = self._calculate_payout(decision.bet_type, decision.amount, won)
            
            # Actualizar bankroll
            bankroll += (payout - decision.amount) if won else -decision.amount
            bankroll_history.append(bankroll)
            
            trades.append({
                'bet_type': decision.bet_type,
                'amount': decision.amount,
                'outcome': actual_next,
                'won': won,
                'profit': payout - decision.amount if won else -decision.amount,
                'bankroll': bankroll
            })
        
        return self._calculate_metrics(trades, bankroll_history, bankroll)
    
    def _calculate_metrics(self, trades: List[Dict], 
                          equity_curve: List[float], 
                          final_bankroll: float) -> BacktestResult:
        """Calcular métricas de rendimiento"""
        
        if not trades:
            return BacktestResult(0, 0, 0, 0, 0, 0, np.array([]), {})
        
        profits = [t['profit'] for t in trades]
        wins = [p for p in profits if p > 0]
        losses = [p for p in profits if p < 0]
        
        total_return = final_bankroll / self.initial_bankroll - 1
        win_rate = len(wins) / len(trades) * 100
        
        # Sharpe ratio
        returns_pct = np.array(profits) / self.initial_bankroll
        sharpe = np.mean(returns_pct) / np.std(returns_pct) * np.sqrt(252) if np.std(returns_pct) > 0 else 0
        
        # Max drawdown
        equity_array = np.array(equity_curve)
        running_max = np.maximum.accumulate(equity_array)
        drawdowns = (equity_array - running_max) / running_max
        max_drawdown = abs(np.min(drawdowns)) * 100
        
        # Profit factor
        gross_profit = sum(wins) if wins else 0
        gross_loss = abs(sum(losses)) if losses else 1
        profit_factor = gross_profit / gross_loss
        
        return BacktestResult(
            total_return=total_return * 100,
            sharpe_ratio=sharpe,
            max_drawdown=max_drawdown,
            win_rate=win_rate,
            profit_factor=profit_factor,
            total_trades=len(trades),
            equity_curve=np.array(equity_curve),
            detailed_stats={
                'trades': trades,
                'gross_profit': gross_profit,
                'gross_loss': gross_loss,
            }
        )
    
    def optimize_hyperparameters(self, 
                                param_grid: Dict,
                                prediction_engine_class,
                                n_iterations: int = 100):
        """Optimizar hiperparámetros con grid search aleatorio"""
        
        from sklearn.model_selection import ParameterSampler
        
        param_list = list(ParameterSampler(param_grid, n_iter=n_iterations))
        results = []
        
        for params in tqdm(param_list, desc="Optimizing"):
            # Configurar motor con nuevos parámetros
            engine = prediction_engine_class(**params)
            
            # Ejecutar backtest
            result = self.run_backtest(
                strategy_func=self._kelly_strategy,
                prediction_engine=engine
            )
            
            results.append({
                'params': params,
                'sharpe': result.sharpe_ratio,
                'return': result.total_return,
                'max_dd': result.max_drawdown
            })
        
        return sorted(results, key=lambda x: x['sharpe'], reverse=True)