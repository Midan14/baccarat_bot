#!/usr/bin/env python3
"""
Baccarat Bot con Web Scraping Agresivo en Tiempo Real
Captura datos de casinos online en tiempo real
"""

import time
import signal
import sys
from datetime import datetime
from playwright.sync_api import sync_playwright
from config.settings import settings
from utils.logger import logger
from core.aggressive_data_acquisition import AggressiveDataAcquisition
from core.prediction_engine import PredictionEngine
from core.decision_engine import DecisionEngine
from utils.helpers import helpers
from utils.telegram_notifier import TelegramNotifier

class BaccaratBotRealTime:
    """Bot con scraping agresivo de datos en tiempo real"""
    
    def __init__(self):
        self.running = False
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        self.data_acquisition = None
        self.prediction_engine = PredictionEngine()
        self.decision_engine = DecisionEngine()
        self.telegram = TelegramNotifier()
        self.iteration = 0
        self.consecutive_errors = 0
        self.max_consecutive_errors = 5
        
        # Configurar manejo de señales
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Manejar señales de terminación"""
        logger.info(f"🛑 Señal {signum} recibida. Deteniendo bot...")
        self.stop()
    
    def initialize_browser(self) -> bool:
        """Inicializar navegador con configuración optimizada"""
        try:
            logger.info("🚀 Inicializando navegador para scraping agresivo...")
            
            self.playwright = sync_playwright().start()
            
            # Configuración agresiva del navegador
            browser_config = {
                "headless": settings.browser.headless,
                "args": [
                    "--disable-blink-features=AutomationControlled",
                    "--disable-dev-shm-usage",
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-web-security",
                    "--disable-features=VizDisplayCompositor",
                    "--disable-accelerated-2d-canvas",
                    "--no-first-run",
                    "--no-zygote",
                    "--disable-gpu",
                    "--disable-dev-shm-usage",
                    "--disable-background-timer-throttling",
                    "--disable-backgrounding-occluded-windows",
                    "--disable-renderer-backgrounding",
                    "--disable-features=TranslateUI",
                    "--disable-ipc-flooding-protection",
                    "--disable-features=site-per-process",
                    "--enable-features=NetworkService,NetworkServiceInProcess"
                ]
            }
            
            self.browser = self.playwright.chromium.launch(**browser_config)
            
            # Contexto con configuración agresiva
            context_config = {
                "viewport": {"width": 1920, "height": 1080},
                "user_agent": settings.browser.user_agent,
                "locale": "es-ES",
                "timezone_id": "America/Bogota",
                "permissions": ["geolocation"],
                "bypass_csp": True,
                "ignore_https_errors": True
            }
            
            self.context = self.browser.new_context(**context_config)
            
            # Configurar interceptación de red
            self.context.route("**/*", self._handle_route)
            
            self.page = self.context.new_page()
            
            # Configurar timeouts agresivos
            self.page.set_default_timeout(30000)
            self.page.set_default_navigation_timeout(30000)
            
            # Configurar interceptación de consola
            self.page.on("console", self._handle_console)
            self.page.on("response", self._handle_response)
            
            logger.info("✅ Navegador inicializado exitosamente")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error inicializando navegador: {str(e)}")
            return False
    
    def _handle_route(self, route):
        """Manejar rutas de red para optimizar carga"""
        if any(resource in route.request.url for resource in ['.jpg', '.png', '.gif', '.css', '.woff']):
            route.abort()
        else:
            route.continue_()
    
    def _handle_console(self, msg):
        """Manejar mensajes de consola"""
        if "error" in msg.text.lower() or "fail" in msg.text.lower():
            logger.debug(f"🖥️ Console: {msg.text}")
    
    def _handle_response(self, response):
        """Manejar respuestas de red"""
        url = response.url.lower()
        if any(keyword in url for keyword in ['history', 'results', 'game', 'round']):
            logger.info(f"🌐 Respuesta capturada: {url}")
    
    def navigate_to_game(self) -> bool:
        """Navegar al juego con estrategias agresivas"""
        try:
            logger.info(f"🎯 Navegando a: {settings.url}")
            
            # Navegación con múltiples estrategias
            navigation_strategies = [
                lambda: self.page.goto(settings.url, wait_until="domcontentloaded", timeout=30000),
                lambda: self.page.goto(settings.url, wait_until="load", timeout=30000),
                lambda: self.page.goto(settings.url, wait_until="networkidle", timeout=30000)
            ]
            
            for strategy in navigation_strategies:
                try:
                    strategy()
                    logger.info("✅ Navegación exitosa")
                    break
                except Exception as e:
                    logger.warning(f"Estrategia de navegación fallida: {str(e)}")
                    continue
            
            # Esperar a que el juego cargue
            time.sleep(3)
            
            # Inicializar adquisición de datos agresiva
            self.data_acquisition = AggressiveDataAcquisition(self.page, self.context)
            
            # Esperar agresivamente al juego
            if not self.data_acquisition.aggressive_wait_for_game():
                logger.error("❌ No se pudo detectar el juego")
                return False
            
            logger.info("✅ Juego detectado y listo")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error navegando al juego: {str(e)}")
            return False
    
    def capture_real_time_data(self) -> bool:
        """Capturar datos en tiempo real con scraping agresivo"""
        try:
            logger.info("🔍 Iniciando captura de datos en tiempo real...")
            
            # Captura agresiva de datos
            game_state = self.data_acquisition.get_game_state_aggressive()
            
            if not game_state or not game_state.get('history'):
                logger.warning("⚠️ No se pudieron capturar datos del juego")
                self.consecutive_errors += 1
                
                if self.consecutive_errors >= self.max_consecutive_errors:
                    logger.error("❌ Demasiados errores consecutivos, deteniendo...")
                    return False
                
                return True  # Continuar intentando
            
            # Resetear contador de errores
            self.consecutive_errors = 0
            
            # Procesar datos capturados
            history = game_state['history']
            logger.info(f"📊 Datos capturados: {len(history)} resultados")
            
            if len(history) > 0:
                logger.info(f"Últimos 10 resultados: {history[-10:]}")
                
                # Analizar y generar señales
                self.process_real_time_data(game_state)
                return True
            else:
                logger.warning("⚠️ Historial vacío capturado")
                return True
                
        except Exception as e:
            logger.error(f"❌ Error capturando datos: {str(e)}")
            self.consecutive_errors += 1
            return self.consecutive_errors < self.max_consecutive_errors
    
    def process_real_time_data(self, game_state: dict):
        """Procesar datos capturados en tiempo real"""
        try:
            self.iteration += 1
            logger.info(f"\n--- ITERACIÓN {self.iteration} ---")
            
            # 1. Extraer historial
            history = game_state['history']
            logger.info(f"📈 Historial capturado: {len(history)} resultados")
            
            if len(history) >= 3:
                logger.info(f"Últimos 5: {history[-5:]}")
            
            # 2. Análisis con motor ML
            prediction = self.prediction_engine.analyze(history)
            
            # 3. Si ML no da señal y hay pocos datos, usar análisis simple
            if prediction.signal == 'NONE' and len(history) >= 3:
                prediction = self.analisis_simple_tendencia(history)
                logger.info("🔄 Usando análisis de tendencia simple")
            
            # 4. Mostrar señal
            logger.info(f"🔮 SEÑAL DETECTADA:")
            logger.info(f"   Señal: {prediction.signal}")
            logger.info(f"   Confianza: {prediction.confidence:.3f}")
            logger.info(f"   Algoritmo: {prediction.algorithm}")
            
            if prediction.probabilities:
                logger.info(f"   Probabilidades: {prediction.probabilities}")
            
            # 5. Tomar decisión
            decision = self.decision_engine.make_decision(prediction, game_state)
            
            # 6. Mostrar decisión
            logger.info(f"💰 DECISIÓN:")
            logger.info(f"   Apostar: {'SÍ' if decision.should_bet else 'NO'}")
            
            if decision.should_bet:
                logger.info(f"   Tipo: {decision.bet_type}")
                logger.info(f"   Monto: ${decision.amount:.2f}")
                logger.info(f"   Confianza: {decision.confidence:.3f}")
                
                # Enviar notificación Telegram
                if settings.telegram.enabled:
                    self.telegram.send_signal_notification(decision, prediction)
            
            # 7. Información del estado del juego
            if game_state.get('time_remaining'):
                logger.info(f"⏰ Tiempo restante: {game_state['time_remaining']}")
            
            if game_state.get('betting_open') is not None:
                logger.info(f"🎲 Apuestas: {'ABIERTAS' if game_state['betting_open'] else 'CERRADAS'}")
            
            # 8. Estadísticas periódicas
            if self.iteration % 10 == 0:
                self.mostrar_estadisticas()
            
        except Exception as e:
            logger.error(f"❌ Error procesando datos: {str(e)}")
    
    def analisis_simple_tendencia(self, history: list):
        """Análisis simple de tendencia para datos en tiempo real"""
        from core.prediction_engine import PredictionResult
        
        if len(history) < 3:
            return PredictionResult(
                signal='NONE',
                confidence=0.0,
                algorithm='insufficient_data',
                probabilities={}
            )
        
        # Análisis de últimos 5 resultados
        last_5 = history[-5:]
        b_count = last_5.count('B')
        p_count = last_5.count('P')
        e_count = last_5.count('E')
        
        total = len(last_5)
        
        # Detectar tendencias
        if b_count >= 3:  # Tendencia a B
            signal = 'B'
            confidence = min(0.7, b_count / total)
        elif p_count >= 3:  # Tendencia a P
            signal = 'P'
            confidence = min(0.7, p_count / total)
        elif e_count >= 2:  # Tendencia a E (menos frecuente)
            signal = 'E'
            confidence = min(0.5, e_count / total)
        else:
            # Sin tendencia clara
            signal = 'NONE'
            confidence = 0.0
        
        probabilities = {
            'B': b_count / total,
            'P': p_count / total,
            'E': e_count / total
        }
        
        return PredictionResult(
            signal=signal,
            confidence=confidence,
            algorithm='real_time_trend',
            probabilities=probabilities
        )
    
    def mostrar_estadisticas(self):
        """Mostrar estadísticas actuales"""
        stats = self.decision_engine.get_stats()
        
        logger.info("\n" + "="*50)
        logger.info("📊 ESTADÍSTICAS DEL BOT EN TIEMPO REAL:")
        logger.info("="*50)
        logger.info(f"   Iteraciones procesadas: {self.iteration}")
        logger.info(f"   Total de apuestas: {stats['total_bets']}")
        logger.info(f"   Ratio de aciertos: {stats['win_rate']:.1f}%")
        logger.info(f"   Bankroll actual: ${stats['current_bankroll']:.2f}")
        logger.info(f"   Profit total: ${stats['profit']:.2f}")
        logger.info(f"   Pérdidas consecutivas: {stats['consecutive_losses']}")
        logger.info("="*50)
    
    def run_real_time(self, max_iterations: int = 100):
        """Ejecutar bot en tiempo real"""
        try:
            logger.info("🚀 INICIANDO BACCARAT BOT EN TIEMPO REAL")
            logger.info("="*60)
            logger.info("🎯 Objetivo: Capturar datos en tiempo real con scraping agresivo")
            logger.info("📊 Se generarán señales basadas en datos reales del juego")
            logger.info("⏰ Actualización cada segundo")
            logger.info("="*60)
            
            self.running = True
            
            # Inicializar navegador
            if not self.initialize_browser():
                return
            
            # Navegar al juego
            if not self.navigate_to_game():
                return
            
            # Bucle principal en tiempo real
            while self.running and self.iteration < max_iterations:
                try:
                    # Capturar datos en tiempo real
                    if not self.capture_real_time_data():
                        break
                    
                    # Pequeña pausa para no sobrecargar
                    time.sleep(1)
                    
                except KeyboardInterrupt:
                    logger.info("⏹️ Interrupción por teclado")
                    break
                except Exception as e:
                    logger.error(f"❌ Error en bucle principal: {str(e)}")
                    time.sleep(5)
            
            # Estadísticas finales
            self.mostrar_estadisticas_finales()
            
        except Exception as e:
            logger.error(f"❌ Error fatal: {str(e)}")
        finally:
            self.stop()
    
    def mostrar_estadisticas_finales(self):
        """Mostrar estadísticas finales"""
        stats = self.decision_engine.get_stats()
        
        logger.info("\n" + "="*60)
        logger.info("🏁 BOT DE TIEMPO REAL FINALIZADO")
        logger.info("="*60)
        logger.info(f"Total de iteraciones: {self.iteration}")
        logger.info(f"Total de apuestas realizadas: {stats['total_bets']}")
        logger.info(f"Ratio de aciertos: {stats['win_rate']:.1f}%")
        logger.info(f"Bankroll final: ${stats['current_bankroll']:.2f}")
        logger.info(f"Profit total: ${stats['profit']:.2f}")
        logger.info(f"ROI: {(stats['profit'] / 1000) * 100:.2f}%")
        logger.info("="*60)
        logger.info("✅ El bot de scraping agresivo ha finalizado")
        logger.info("✅ Se capturaron datos en tiempo real del juego")
    
    def stop(self):
        """Detener el bot gracefulmente"""
        logger.info("🛑 Deteniendo Baccarat Bot en tiempo real...")
        self.running = False
        
        if self.browser:
            self.browser.close()
        
        if self.playwright:
            self.playwright.stop()
        
        logger.info("✅ Bot detenido exitosamente")

def main():
    """Función principal"""
    bot = BaccaratBotRealTime()
    
    try:
        bot.run_real_time(max_iterations=50)  # 50 iteraciones para prueba
    except KeyboardInterrupt:
        logger.info("⏹️ Interrupción por teclado recibida")
    except Exception as e:
        logger.error(f"❌ Error fatal: {str(e)}")
    finally:
        bot.stop()

if __name__ == "__main__":
    main()