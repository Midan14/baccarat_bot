# config/lightning_dragontiger_config.py
"""
Configuración específica para Lightning Dragon Tiger de Evolution Gaming
https://20bet.com/es/live-casino/game/evolution/lightningdragontiger
"""

from dataclasses import dataclass, field
from typing import Dict, List

@dataclass
class LightningDragonTigerConfig:
    """Configuración específica para Lightning Dragon Tiger"""
    
    # URL del juego
    game_url: str = ("https://20bet.com/es/live-casino/game/"
                    "evolution/lightningdragontiger")
    
    # Configuración del juego
    game_type: str = "lightning_dragontiger"
    provider: str = "evolution"
    
    # Opciones de apuesta específicas del juego
    bet_options: List[str] = field(default_factory=lambda: ["Dragon", "Tiger", "Tie"])
    
    # Pagos según el tipo de apuesta
    payouts: Dict[str, float] = field(default_factory=lambda: {
        "Dragon": 1.0,    # 1:1
        "Tiger": 1.0,     # 1:1
        "Tie": 11.0       # 11:1 (puede variar según el casino)
    })
    
    # Configuración específica de Lightning (multiplicadores)
    lightning_multipliers: Dict[str, List[int]] = field(default_factory=lambda: {
        "Dragon": [2, 3, 5, 8, 10],
        "Tiger": [2, 3, 5, 8, 10],
        "Tie": [2, 3, 5, 8, 10, 15, 20, 25, 50]
    })
    
    # Probabilidades aproximadas
    probabilities: Dict[str, float] = field(default_factory=lambda: {
        "Dragon": 0.446,  # 44.6%
        "Tiger": 0.446,   # 44.6%
        "Tie": 0.108      # 10.8%
    })
    
    # Selectores CSS específicos para este juego
    selectors: Dict[str, str] = field(default_factory=lambda: {
        "game_area": ".game-area",
        "dragon_area": ".dragon-area",
        "tiger_area": ".tiger-area",
        "tie_area": ".tie-area",
        "history_panel": ".history-panel",
        "result_display": ".result-display",
        "betting_controls": ".betting-controls",
        "chip_selector": ".chip-selector",
        "place_bet_button": ".place-bet-button",
        "clear_bet_button": ".clear-bet-button",
        "balance_display": ".balance-display",
        "timer_display": ".timer-display"
    })
    
    # Timing específico del juego
    betting_time: int = 15  # segundos para apostar
    result_display_time: int = 5  # segundos para mostrar resultado
    new_round_delay: int = 3  # segundos entre rondas

# Instancia de configuración
lightning_dragontiger_config = LightningDragonTigerConfig()