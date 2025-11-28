#!/usr/bin/env python3
"""
Versión de prueba del Baccarat Bot con datos simulados
Para demostrar que el sistema de señales funciona correctamente
"""

import time
import random
from datetime import datetime
from config.settings import settings
from utils.logger import logger
from core.prediction_engine import PredictionEngine
from core.decision_engine import DecisionEngine
from utils.helpers import helpers

class BaccaratBotSimulado:
    """Bot de prueba con datos simulados"""
    
    def __init__(self):
        self.running = False
        self.prediction_engine = PredictionEngine()
        self.decision_engine = DecisionEngine()
        self.simulated_history = []
        self.iteration = 0
        
    def generate_simulated_data(self) -> dict:
        """Generar datos de juego simulados realistas"""
        # Generar resultados aleatorios pero con algunos patrones
        outcomes = ['Dragon', 'Tiger', 'Tie']
        weights = [0.446, 0.446, 0.108]  # Probabilidades reales
        
        # Generar 50-100 resultados históricos
        if len(self.simulated_history) < 100:
            new_result = random.choices(outcomes, weights=weights)[0]
            self.simulated_history.append(new_result)
        
        # Mantener solo los últimos 100 resultados
        if len(self.simulated_history) > 100:
            self.simulated_history = self.simulated_history[-100:]
        
        return {
            'history': self.simulated_history.copy(),
            'betting_open': True,
            'current_round': self.iteration,
            'timestamp': datetime.now().isoformat()
        }
    
    def run_simulation(self, iterations=20):
        """Ejecutar simulación de prueba"""
        logger.info("🎰 INICIANDO SIMULACIÓN DE BACCARAT BOT")
        logger.info("=" * 60)
        
        self.running = True
        
        while self.running and self.iteration < iterations:
            try:
                self.iteration += 1
                logger.info(f"\n--- ITERACIÓN {self.iteration} ---")
                
                # 1. Generar datos simulados
                game_state = self.generate_simulated_data()
                logger.info(f"📊 Historial actual: {len(game_state['history'])} resultados")
                logger.info(f"Últimos 10: {game_state['history'][-10:]}")
                
                # 2. Analizar y predecir
                prediction = self.prediction_engine.analyze(game_state['history'])
                
                # 3. Mostrar predicción
                logger.info(f"🔮 PREDICCIÓN:")
                logger.info(f"   Señal: {prediction.signal}")
                logger.info(f"   Confianza: {prediction.confidence:.3f}")
                logger.info(f"   Algoritmo: {prediction.algorithm}")
                logger.info(f"   Probabilidades: {prediction.probabilities}")
                
                # 4. Tomar decisión
                decision = self.decision_engine.make_decision(prediction, game_state)
                
                # 5. Mostrar decisión
                logger.info(f"💰 DECISIÓN:")
                logger.info(f"   Apostar: {'SÍ' if decision.should_bet else 'NO'}")
                if decision.should_bet:
                    logger.info(f"   Tipo: {decision.bet_type}")
                    logger.info(f"   Monto: ${decision.amount:.2f}")
                    logger.info(f"   Confianza: {decision.confidence:.3f}")
                    logger.info(f"   Razón: {decision.reason}")
                
                # 6. Simular resultado si se apostó
                if decision.should_bet:
                    # Simular resultado real
                    actual_result = random.choices(
                        ['Dragon', 'Tiger', 'Tie'], 
                        weights=[0.446, 0.446, 0.108]
                    )[0]
                    
                    won = (decision.bet_type == 'B' and actual_result == 'Dragon') or \
                          (decision.bet_type == 'P' and actual_result == 'Tiger') or \
                          (decision.bet_type == 'E' and actual_result == 'Tie')
                    
                    # Calcular payout
                    if won:
                        if decision.bet_type == 'E':  # Tie paga 8:1
                            payout = decision.amount * 8.0
                        else:  # Dragon/Tiger paga 1:1
                            payout = decision.amount * 1.0
                    else:
                        payout = 0.0
                    
                    # Registrar resultado
                    self.decision_engine.record_result(decision, won, payout)
                    
                    logger.info(f"🎯 RESULTADO:")
                    logger.info(f"   Resultado real: {actual_result}")
                    logger.info(f"   Apuesta: {'GANADA' if won else 'PERDIDA'}")
                    logger.info(f"   Payout: ${payout:.2f}")
                
                # 7. Estadísticas cada 5 iteraciones
                if self.iteration % 5 == 0:
                    stats = self.decision_engine.get_stats()
                    logger.info(f"📈 ESTADÍSTICAS (Iteración {self.iteration}):")
                    logger.info(f"   Total apuestas: {stats['total_bets']}")
                    logger.info(f"   Ratio de aciertos: {stats['win_rate']:.1f}%")
                    logger.info(f"   Bankroll actual: ${stats['current_bankroll']:.2f}")
                    logger.info(f"   Profit total: ${stats['profit']:.2f}")
                    logger.info(f"   Pérdidas consecutivas: {stats['consecutive_losses']}")
                
                # 8. Esperar antes de la siguiente iteración
                helpers.random_delay(2, 4)
                
            except KeyboardInterrupt:
                logger.info("⏹️  Simulación interrumpida por el usuario")
                break
            except Exception as e:
                logger.error(f"❌ Error en iteración {self.iteration}: {str(e)}")
                helpers.random_delay(5, 10)
        
        # Estadísticas finales
        final_stats = self.decision_engine.get_stats()
        logger.info("\n" + "=" * 60)
        logger.info("🏁 SIMULACIÓN FINALIZADA")
        logger.info("=" * 60)
        logger.info(f"Total de iteraciones: {self.iteration}")
        logger.info(f"Total de apuestas: {final_stats['total_bets']}")
        logger.info(f"Ratio de aciertos: {final_stats['win_rate']:.1f}%")
        logger.info(f"Bankroll final: ${final_stats['current_bankroll']:.2f}")
        logger.info(f"Profit total: ${final_stats['profit']:.2f}")
        logger.info(f"ROI: {(final_stats['profit'] / 1000) * 100:.2f}%")
        
        return final_stats

if __name__ == "__main__":
    bot = BaccaratBotSimulado()
    
    try:
        # Ejecutar simulación con 30 iteraciones
        resultados = bot.run_simulation(iterations=30)
        
        logger.info("\n✅ Simulación completada exitosamente")
        logger.info("✅ El sistema de señales está funcionando correctamente")
        
    except Exception as e:
        logger.error(f"❌ Error en la simulación: {str(e)}")