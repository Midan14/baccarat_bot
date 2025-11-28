# main.py
import time
import signal
import sys
from typing import Optional
from config.settings import settings
from utils.logger import logger
from utils.helpers import helpers
from core.browser import StealthBrowser
from core.data_acquisition import DataAcquisition
from core.prediction_engine import PredictionEngine
from core.decision_engine import DecisionEngine
from core.execution_engine import ExecutionEngine
from core.decision_engine import BettingDecision

class BaccaratBot:
    """Bot principal de Baccarat"""
    
    def __init__(self):
        self.running = False
        self.browser_manager: Optional[StealthBrowser] = None
        self.data_acquisition: Optional[DataAcquisition] = None
        self.prediction_engine: Optional[PredictionEngine] = None
        self.decision_engine: Optional[DecisionEngine] = None
        self.execution_engine: Optional[ExecutionEngine] = None
        self.page = None
        
        # Configurar manejo de señales para shutdown graceful
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Manejar señales de terminación"""
        logger.info(f"Recibida señal {signum}. Cerrando...")
        self.stop()
    
    def initialize(self) -> bool:
        """Inicializar todos los componentes del bot"""
        try:
            logger.info("Inicializando Baccarat Bot...")
            
            # 1. Navegador
            self.browser_manager = StealthBrowser()
            self.page, browser = self.browser_manager.start()
            
            # 2. Navegar a la URL
            logger.info(f"Navegando a {settings.url}")
            self.page.goto(settings.url)
            
            # 3. Inicializar componentes
            self.data_acquisition = DataAcquisition(self.page)
            self.prediction_engine = PredictionEngine()
            self.decision_engine = DecisionEngine()
            self.execution_engine = ExecutionEngine(self.page)
            
            # 4. Esperar a que el juego cargue
            if not self.data_acquisition.wait_for_game_load():
                logger.error("No se pudo cargar el juego")
                return False
            
            logger.info("Bot inicializado exitosamente")
            return True
            
        except Exception as e:
            logger.error(f"Error inicializando bot: {str(e)}", exc_info=True)
            return False
    
    def run(self):
        """Ejecutar el bucle principal del bot"""
        if not self.initialize():
            logger.error("No se pudo inicializar el bot")
            return
        
        self.running = True
        iteration = 0
        
        logger.info("Iniciando bucle principal de apuestas...")
        
        while self.running:
            try:
                iteration += 1
                logger.info(f"--- Iteración {iteration} ---")
                
                # 1. Adquirir datos del juego
                game_state = self.data_acquisition.get_game_state()
                if not game_state or not game_state.get('history'):
                    logger.warning("No se pudieron obtener datos del juego")
                    helpers.random_delay(5, 10)
                    continue
                
                # 2. Analizar y predecir
                prediction = self.prediction_engine.analyze(game_state['history'])
                
                # 3. Tomar decisión
                decision = self.decision_engine.make_decision(prediction, game_state)
                
                # 4. Ejecutar apuesta si corresponde
                if decision.should_bet:
                    bet_placed = self.execution_engine.place_bet(decision)
                    
                    # 5. Simular resultado (en un bot real, aquí se esperaría el resultado real)
                    # Por ahora, simulamos un resultado aleatorio para testing
                    if bet_placed:
                        self._simulate_game_result(decision)
                
                # 6. Mostrar estadísticas periódicamente
                if iteration % 10 == 0:
                    self._log_statistics()
                
                # 7. Esperar antes de la siguiente iteración
                helpers.random_delay(3, 8)
                
            except Exception as e:
                logger.error(f"Error en iteración {iteration}: {str(e)}", exc_info=True)
                helpers.random_delay(10, 15)
                
                # Tomar captura de pantalla para debugging
                if self.browser_manager:
                    self.browser_manager.take_screenshot(f"error_iteration_{iteration}")
    
    def _simulate_game_result(self, decision: BettingDecision):
        """Simular resultado del juego (para testing)"""
        import random
        
        # Simular resultado aleatorio (45% Banker, 45% Player, 10% Tie)
        outcomes = ['B', 'B', 'P', 'P', 'E']
        actual_result = random.choice(outcomes)
        
        # Calcular si ganó
        won = (decision.bet_type == actual_result)
        
        # Calcular payout
        if won:
            if decision.bet_type == 'B':
                payout = decision.amount * 0.95  # Comisión 5%
            elif decision.bet_type == 'P':
                payout = decision.amount * 1.0
            else:  # Tie
                payout = decision.amount * 8.0  # Pago 8:1
        else:
            payout = 0
        
        # Registrar resultado
        self.decision_engine.record_result(decision, won, payout)
        
        logger.info(f"Resultado simulado: {actual_result} - "
                   f"Apuesta: {decision.bet_type} - "
                   f"{'GANADA' if won else 'PERDIDA'}")
    
    def _log_statistics(self):
        """Mostrar estadísticas actuales"""
        stats = self.decision_engine.get_stats()
        exec_stats = self.execution_engine.get_execution_stats()
        
        logger.info("📊 ESTADÍSTICAS ACTUALES:")
        logger.info(f"   Apuestas totales: {stats['total_bets']}")
        logger.info(f"   Ratio de aciertos: {stats['win_rate']:.1f}%")
        logger.info(f"   Bankroll actual: {stats['current_bankroll']:.2f}")
        logger.info(f"   Profit total: {stats['profit']:.2f}")
        logger.info(f"   Ejecuciones: {exec_stats['total_executions']}")
        logger.info(f"   Pérdidas consecutivas: {stats['consecutive_losses']}")
    
    def stop(self):
        """Detener el bot gracefulmente"""
        logger.info("Deteniendo Baccarat Bot...")
        self.running = False
        
        if self.browser_manager:
            self.browser_manager.stop()
        
        logger.info("Bot detenido exitosamente")
        sys.exit(0)

def main():
    """Función principal"""
    bot = BaccaratBot()
    
    try:
        bot.run()
    except KeyboardInterrupt:
        logger.info("Interrupción por teclado recibida")
    except Exception as e:
        logger.error(f"Error fatal: {str(e)}", exc_info=True)
    finally:
        bot.stop()

if __name__ == "__main__":
    main()