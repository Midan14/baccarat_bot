#!/usr/bin/env python3
"""
Baccarat Bot Avanzado Completo
Integra todas las mejoras: IA, Monte Carlo, señales inteligentes y gestión de riesgos
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging
import signal
import sys

# Importar componentes avanzados
from core.neural_networks import EnsemblePredictor, PatternAnalyzer
from core.monte_carlo import MonteCarloEngine, BayesianUpdater
from core.signal_generator import SignalManager, GameData
from core.risk_management import RiskManager, BankrollState
from core.data_acquisition import DataAggregator, LiveCasinoAPI, create_casino_connection
from utils.telegram_notifier import TelegramNotifier
from utils.logger import setup_logger

# Configuración de logging
logger = setup_logger('baccarat_bot_advanced')

class AdvancedBaccaratBot:
    """Bot principal con todas las características avanzadas"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.running = False
        self.paused = False
        
        # Componentes principales
        self.signal_manager = None
        self.risk_manager = None
        self.data_aggregator = None
        self.telegram_bot = None
        
        # Estado del bot
        self.session_data = {
            'start_time': None,
            'hands_played': 0,
            'signals_generated': 0,
            'total_profit': 0.0,
            'success_rate': 0.0
        }
        
        # Configuración
        self.bet_confirmation_delay = config.get('bet_confirmation_delay', 3)
        self.signal_frequency = config.get('signal_frequency', 7)  # Cada 7 manos
        self.max_session_duration = config.get('max_session_duration', 7200)  # 2 horas
        
    async def initialize(self):
        """Inicializa todos los componentes del bot"""
        try:
            logger.info("Inicializando Baccarat Bot Avanzado...")
            
            # 1. Configurar Telegram
            if self.config.get('telegram', {}).get('enabled', False):
                self.telegram_bot = TelegramNotifier(
                    token=self.config['telegram']['bot_token'],
                    chat_id=self.config['telegram']['chat_id']
                )
                logger.info("Telegram configurado")
            
            # 2. Crear gestor de riesgos
            self.risk_manager = RiskManager(
                initial_bankroll=self.config['bankroll']['initial_amount'],
                base_unit=self.config['bankroll']['base_unit']
            )
            logger.info("Gestor de riesgos inicializado")
            
            # 3. Crear generador de señales
            self.signal_manager = SignalManager(self.telegram_bot)
            logger.info("Generador de señales inicializado")
            
            # 4. Configurar adquisición de datos
            await self._setup_data_sources()
            logger.info("Fuentes de datos configuradas")
            
            # 5. Entrenar modelos si es necesario
            await self._train_models()
            logger.info("Modelos entrenados")
            
            logger.info("✅ Bot avanzado inicializado exitosamente")
            
        except Exception as e:
            logger.error(f"Error inicializando bot: {e}")
            raise
    
    async def _setup_data_sources(self):
        """Configura fuentes de datos"""
        self.data_aggregator = DataAggregator()
        
        # Agregar fuentes de datos configuradas
        for source_config in self.config.get('data_sources', []):
            if source_config['enabled']:
                try:
                    source = create_casino_connection(
                        source_config['casino_name'],
                        source_config['api_key']
                    )
                    self.data_aggregator.add_source(source)
                    logger.info(f"Fuente agregada: {source_config['casino_name']}")
                except Exception as e:
                    logger.error(f"Error agregando fuente {source_config['casino_name']}: {e}")
    
    async def _train_models(self):
        """Entrena modelos de IA si es necesario"""
        # Verificar si hay datos históricos para entrenamiento
        training_data = await self._load_training_data()
        
        if training_data and len(training_data) > 100:
            logger.info(f"Entrenando modelos con {len(training_data)} registros...")
            
            # Entrenar ensamble de predictores
            self.signal_manager.signal_generator.ensemble_predictor.train_all_models(training_data)
            
            logger.info("✅ Modelos entrenados con datos históricos")
        else:
            logger.info("Usando modelos pre-entrenados (modo demo)")
    
    async def _load_training_data(self) -> List[Dict]:
        """Carga datos de entrenamiento"""
        # Implementar carga de datos históricos
        # Por ahora, retornar lista vacía para usar modelos demo
        return []
    
    async def start(self):
        """Inicia el bot"""
        try:
            logger.info("🚀 Iniciando Baccarat Bot Avanzado...")
            
            self.running = True
            self.session_data['start_time'] = datetime.now()
            
            # Iniciar sesión de riesgo
            self.risk_manager.start_session()
            
            # Configurar manejo de señales
            self._setup_signal_handlers()
            
            # Iniciar recolección de datos
            data_task = asyncio.create_task(self.data_aggregator.start_collection())
            
            # Iniciar procesamiento principal
            processing_task = asyncio.create_task(self._main_processing_loop())
            
            # Iniciar monitoreo
            monitoring_task = asyncio.create_task(self._monitoring_loop())
            
            # Esperar a que terminen las tareas
            await asyncio.gather(data_task, processing_task, monitoring_task)
            
        except Exception as e:
            logger.error(f"Error en bot principal: {e}")
            self.stop()
    
    def stop(self):
        """Detiene el bot"""
        logger.info("🛑 Deteniendo Baccarat Bot...")
        self.running = False
        
        if self.risk_manager:
            self.risk_manager.end_session()
        
        # Guardar estadísticas
        self._save_session_stats()
        
        logger.info("✅ Bot detenido exitosamente")
    
    def pause(self):
        """Pausa el bot"""
        logger.info("⏸️ Bot pausado")
        self.paused = True
    
    def resume(self):
        """Reanuda el bot"""
        logger.info("▶️ Bot reanudado")
        self.paused = False
    
    async def _main_processing_loop(self):
        """Bucle principal de procesamiento"""
        logger.info("Iniciando bucle de procesamiento principal...")
        
        while self.running:
            try:
                if self.paused:
                    await asyncio.sleep(1)
                    continue
                
                # Verificar si se debe continuar la sesión
                if not self.risk_manager.should_continue_session():
                    logger.warning("Condiciones para detener sesión detectadas")
                    self.stop()
                    break
                
                # Obtener datos recientes
                recent_data = self.data_aggregator.get_recent_data(count=10)
                
                if recent_data:
                    # Procesar cada nuevo dato
                    for game_data in recent_data:
                        await self._process_game_data(game_data)
                
                # Esperar antes de siguiente iteración
                await asyncio.sleep(2)  # 2 segundos entre iteraciones
                
            except Exception as e:
                logger.error(f"Error en bucle principal: {e}")
                await asyncio.sleep(5)  # Esperar antes de reintentar
    
    async def _process_game_data(self, game_data: GameData):
        """Procesa datos de juego individual"""
        try:
            # Validar datos
            if not self._validate_game_data(game_data):
                return
            
            # Actualizar contadores
            self.session_data['hands_played'] += 1
            
            # Procesar con el gestor de señales
            self.signal_manager.process_new_game_data(game_data)
            
            # Verificar si hay señales activas
            active_signals = self.signal_manager.get_recent_signals(count=5)
            
            for signal_data in active_signals:
                await self._execute_signal(signal_data, game_data)
            
        except Exception as e:
            logger.error(f"Error procesando datos de juego: {e}")
    
    async def _execute_signal(self, signal_data: Dict, game_data: GameData):
        """Ejecuta una señal de apuesta"""
        try:
            # Verificar confianza
            confidence = signal_data.get('confidence')
            if confidence not in ['HIGH', 'MEDIUM']:
                logger.debug(f"Señal con baja confianza omitida: {confidence}")
                return
            
            # Calcular tamaño de apuesta
            win_probability = max(signal_data.get('monte_carlo_probs', {}).values())
            bet_recommendation = self.risk_manager.get_bet_sizing_recommendation(
                win_probability, confidence
            )
            
            bet_size = bet_recommendation['recommended_bet_size']
            
            if bet_size <= 0:
                logger.debug("Tamaño de apuesta cero, omitiendo")
                return
            
            # Confirmar apuesta
            if await self._confirm_bet(signal_data, bet_size):
                # Registrar apuesta
                self.risk_manager.record_bet_result(bet_size, 0, 'pending')
                
                # Esperar resultado
                await self._wait_for_result(signal_data, game_data)
                
                logger.info(f"Apuesta ejecutada: {signal_data['recommended_bet']} - ${bet_size:.2f}")
                
        except Exception as e:
            logger.error(f"Error ejecutando señal: {e}")
    
    async def _confirm_bet(self, signal_data: Dict, bet_size: float) -> bool:
        """Confirma una apuesta antes de ejecutar"""
        try:
            # En modo real, aquí iría la lógica de confirmación
            # Por ahora, confirmar automáticamente con delay
            
            if self.bet_confirmation_delay > 0:
                await asyncio.sleep(self.bet_confirmation_delay)
            
            # Verificar que la señal siga siendo válida
            current_time = datetime.now()
            signal_time = datetime.fromisoformat(signal_data['timestamp'])
            
            if (current_time - signal_time).total_seconds() > 30:  # Máximo 30 segundos
                logger.warning("Señal expirada")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error confirmando apuesta: {e}")
            return False
    
    async def _wait_for_result(self, signal_data: Dict, game_data: GameData):
        """Espera y registra el resultado de una apuesta"""
        try:
            # Determinar si la apuesta fue ganadora
            recommended_bet = signal_data['recommended_bet']
            actual_result = game_data.result
            
            is_winner = (recommended_bet == actual_result)
            
            # Calcular resultado
            bet_size = signal_data['bet_size'] * self.config['bankroll']['base_unit']
            
            if is_winner:
                if recommended_bet == 'T':  # Tie paga 8:1
                    result = bet_size * 8
                elif recommended_bet == 'B':  # Banker paga 0.95:1
                    result = bet_size * 0.95
                else:  # Player paga 1:1
                    result = bet_size * 1
            else:
                result = -bet_size
            
            # Registrar resultado
            self.risk_manager.record_bet_result(bet_size, result, actual_result)
            
            # Actualizar estadísticas
            self.session_data['total_profit'] += result
            
            logger.info(f"Resultado: {actual_result} - ${result:+.2f}")
            
        except Exception as e:
            logger.error(f"Error procesando resultado: {e}")
    
    async def _monitoring_loop(self):
        """Bucle de monitoreo y reportes"""
        logger.info("Iniciando monitoreo...")
        
        while self.running:
            try:
                # Reporte cada 5 minutos
                await asyncio.sleep(300)  # 5 minutos
                
                if not self.paused:
                    await self._generate_status_report()
                    
            except Exception as e:
                logger.error(f"Error en monitoreo: {e}")
    
    async def _generate_status_report(self):
        """Genera reporte de estado"""
        try:
            # Obtener estadísticas
            risk_stats = self.risk_manager.get_risk_assessment()
            signal_stats = self.signal_manager.get_signal_statistics()
            
            # Calcular tiempo de sesión
            session_duration = datetime.now() - self.session_data['start_time']
            
            report = f"""
📊 REPORTE DE ESTADO - BACCARAT BOT AVANZADO

⏱️  TIEMPO DE SESIÓN: {session_duration.total_seconds()/3600:.1f} horas
🎯 MANOS PROCESADAS: {self.session_data['hands_played']}
📈 SÑALES GENERADAS: {self.session_data['signals_generated']}
💰 BENEFICIO TOTAL: ${self.session_data['total_profit']:+.2f}

🏦 BANKROLL ACTUAL: ${risk_stats['current_bankroll']:.2f}
📉 DRAWDOWN MÁXIMO: {risk_stats['max_drawdown']:.1%}
📊 VOLATILIDAD: {risk_stats['current_volatility']:.2f}
🎲 RACHA ACTUAL: {risk_stats['current_streak']}
            """
            
            # Enviar reporte
            if self.telegram_bot:
                self.telegram_bot.send_message(report)
            
            logger.info(report)
            
        except Exception as e:
            logger.error(f"Error generando reporte: {e}")
    
    def _validate_game_data(self, game_data: GameData) -> bool:
        """Valida datos de juego"""
        try:
            # Validaciones básicas
            if not game_data.result in ['B', 'P', 'T']:
                return False
                
            if not (0 <= game_data.banker_score <= 9):
                return False
                
            if not (0 <= game_data.player_score <= 9):
                return False
                
            return True
            
        except Exception:
            return False
    
    def _setup_signal_handlers(self):
        """Configura manejo de señales del sistema"""
        def signal_handler(signum, frame):
            logger.info(f"Señal recibida: {signum}")
            self.stop()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    def _save_session_stats(self):
        """Guarda estadísticas de la sesión"""
        try:
            stats = {
                'session_data': self.session_data,
                'final_bankroll': self.risk_manager.current_bankroll if self.risk_manager else 0,
                'end_time': datetime.now().isoformat(),
                'config': self.config
            }
            
            filename = f"session_stats_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w') as f:
                json.dump(stats, f, indent=2, default=str)
                
            logger.info(f"Estadísticas guardadas en: {filename}")
            
        except Exception as e:
            logger.error(f"Error guardando estadísticas: {e}")


def load_config() -> Dict:
    """Carga configuración del bot"""
    return {
        'bankroll': {
            'initial_amount': 1000.0,
            'base_unit': 10.0
        },
        'telegram': {
            'enabled': True,
            'bot_token': 'YOUR_BOT_TOKEN',
            'chat_id': 'YOUR_CHAT_ID'
        },
        'data_sources': [
            {
                'enabled': True,
                'casino_name': 'evolution_gaming',
                'api_key': 'YOUR_API_KEY'
            }
        ],
        'bet_confirmation_delay': 3,
        'signal_frequency': 7,
        'max_session_duration': 7200
    }


async def main():
    """Función principal"""
    try:
        # Cargar configuración
        config = load_config()
        
        # Crear bot
        bot = AdvancedBaccaratBot(config)
        
        # Inicializar
        await bot.initialize()
        
        # Iniciar
        await bot.start()
        
    except Exception as e:
        logger.error(f"Error en función principal: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # Ejecutar bot
    asyncio.run(main())