# core/prediction_engine.py
"""
Motor de predicción para Lightning Dragon Tiger
Mantene compatibilidad con el código existente mientras usa el motor específico
"""

from core.lightning_dragontiger_engine import (
    LightningDragonTigerEngine,
    DragonTigerPrediction,
    GameState
)
from typing import List
from utils.logger import logger
from utils.telegram_notifier import telegram_notifier


class PredictionEngine:
    """Motor de predicción que envuelve LightningDragonTigerEngine"""
    
    def __init__(self):
        self.engine = LightningDragonTigerEngine()
        self.name = "Lightning Dragon Tiger Prediction Engine"
        
    def analyze(self, history: List[str]) -> DragonTigerPrediction:
        """
        Analizar historial y generar predicción
        Mantiene la interfaz compatible con el código existente
        """
        logger.info("Iniciando análisis de predicción para "
                    "Lightning Dragon Tiger...")
        
        # Crear GameState con el historial proporcionado
        # Los otros campos se inicializan con valores por defecto
        game_state = GameState(
            history=history,
            dragon_cards=[],
            tiger_cards=[],
            lightning_multipliers={},
            current_round=len(history),
            betting_open=True
        )
        
        # Usar el motor específico de Lightning Dragon Tiger
        prediction = self.engine.analyze(game_state)
        
        logger.info(f"Predicción generada: {prediction.signal} "
                    f"(confianza: {prediction.confidence:.2f})")
        
        # Enviar notificación a Telegram
        try:
            telegram_notifier.send_prediction_signal(
                game_type="Lightning Dragon Tiger",
                prediction=prediction.signal,
                confidence=prediction.confidence * 100,  # Convertir a %
                reasoning=prediction.reasoning,
                additional_info={
                    "Ronda": len(history),
                    "Historial": len(history)
                }
            )
        except Exception as e:
            logger.error(f"Error al enviar notificación a Telegram: {e}")
        
        return prediction
    
    def get_name(self) -> str:
        """Obtener nombre del motor"""
        return self.name
    
    def get_game_type(self) -> str:
        """Obtener tipo de juego"""
        return "lightning_dragontiger"


# Alias para mantener compatibilidad
Prediction = DragonTigerPrediction
PredictionResult = DragonTigerPrediction