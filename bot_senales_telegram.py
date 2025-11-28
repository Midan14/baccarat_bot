#!/usr/bin/env python3
"""
Bot de Señales de Baccarat para Telegram
Envía señales en tiempo real directamente a Telegram
"""

import asyncio
import json
import time
from datetime import datetime
from typing import Dict, List
import logging

from core.signal_generator import SignalManager, Signal
from core.data_acquisition import DataAggregator, create_casino_connection
from utils.telegram_notifier import TelegramNotifier
from utils.logger import setup_logger

logger = setup_logger('telegram_signals_bot')

class TelegramSignalsBot:
    """Bot especializado en envío de señales por Telegram"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.running = False
        
        # Componentes
        self.telegram_bot = None
        self.signal_manager = None
        self.data_aggregator = None
        
        # Estadísticas
        self.stats = {
            'signals_sent': 0,
            'high_confidence_signals': 0,
            'total_profit': 0.0,
            'success_rate': 0.0,
            'start_time': None
        }
        
    async def initialize(self):
        """Inicializa el bot de señales"""
        try:
            logger.info("🚀 Inicializando Bot de Señales Telegram...")
            
            # 1. Configurar Telegram
            telegram_config = self.config['telegram']
            self.telegram_bot = TelegramNotifier(
                token=telegram_config['bot_token'],
                chat_id=telegram_config['chat_id']
            )
            
            # Verificar conexión Telegram
            await self.telegram_bot.test_connection()
            logger.info("✅ Telegram conectado")
            
            # 2. Crear gestor de señales
            self.signal_manager = SignalManager(self.telegram_bot)
            logger.info("✅ Gestor de señales inicializado")
            
            # 3. Configurar fuentes de datos
            await self._setup_data_sources()
            logger.info("✅ Fuentes de datos configuradas")
            
            # 4. Mensaje de bienvenida
            await self._send_welcome_message()
            
            logger.info("✅ Bot de señales inicializado exitosamente")
            
        except Exception as e:
            logger.error(f"Error inicializando bot de señales: {e}")
            raise
    
    async def _setup_data_sources(self):
        """Configura fuentes de datos"""
        self.data_aggregator = DataAggregator()
        
        for source_config in self.config.get('data_sources', []):
            if source_config['enabled']:
                try:
                    source = create_casino_connection(
                        source_config['casino_name'],
                        source_config['api_key']
                    )
                    self.data_aggregator.add_source(source)
                    logger.info(f"Fuente conectada: {source_config['casino_name']}")
                except Exception as e:
                    logger.error(f"Error conectando {source_config['casino_name']}: {e}")
    
    async def _send_welcome_message(self):
        """Envía mensaje de bienvenida"""
        welcome_msg = f"""
🎯 *BACCARAT SIGNALS BOT INICIADO*

✅ Conectado a casinos en vivo
🧠 IA avanzada activada
📊 Análisis en tiempo real
💰 Gestión de riesgos inteligente

🚀 *Listo para generar señales de alta precisión*

Configuración:
• Frecuencia: Cada 6-8 manos
• Confianza mínima: {self.config.get('min_confidence', 'MEDIUM')}
• Banco de datos: {len(self.config.get('data_sources', []))} casinos
        """
        
        await self.telegram_bot.send_message(welcome_msg)
    
    async def start(self):
        """Inicia el bot de señales"""
        try:
            logger.info("🚀 Iniciando Bot de Señales...")
            
            self.running = True
            self.stats['start_time'] = datetime.now()
            
            # Iniciar recolección de datos
            data_task = asyncio.create_task(self.data_aggregator.start_collection())
            
            # Iniciar procesamiento de señales
            signals_task = asyncio.create_task(self._signals_processing_loop())
            
            # Iniciar reportes periódicos
            reports_task = asyncio.create_task(self._periodic_reports_loop())
            
            # Esperar tareas
            await asyncio.gather(data_task, signals_task, reports_task)
            
        except Exception as e:
            logger.error(f"Error en bot de señales: {e}")
            await self.stop()
    
    async def stop(self):
        """Detiene el bot"""
        logger.info("🛑 Deteniendo Bot de Señales...")
        self.running = False
        
        # Mensaje de despedida
        goodbye_msg = f"""
🔴 *BOT DE SEÑALES DETENIDO*

📊 Estadísticas finales:
• Señales enviadas: {self.stats['signals_sent']}
• Señales de alta confianza: {self.stats['high_confidence_signals']}
• Beneficio total: ${self.stats['total_profit']:+.2f}
• Tasa de acierto: {self.stats['success_rate']:.1%}

💰 *¡Gracias por usar nuestro bot!*
        """
        
        await self.telegram_bot.send_message(goodbye_msg)
        
        # Guardar estadísticas
        self._save_stats()
        
        logger.info("✅ Bot de señales detenido")
    
    async def _signals_processing_loop(self):
        """Bucle principal de procesamiento de señales"""
        logger.info("Iniciando bucle de procesamiento de señales...")
        
        while self.running:
            try:
                # Obtener datos recientes
                recent_data = self.data_aggregator.get_recent_data(count=20)
                
                if recent_data:
                    # Procesar cada nuevo dato
                    for game_data in recent_data[-5:]:  # Últimos 5 juegos
                        await self._process_for_signals(game_data)
                
                # Esperar antes de siguiente iteración
                await asyncio.sleep(3)  # 3 segundos
                
            except Exception as e:
                logger.error(f"Error en bucle de señales: {e}")
                await asyncio.sleep(5)
    
    async def _process_for_signals(self, game_data):
        """Procesa datos de juego para generar señales"""
        try:
            # Procesar con el gestor de señales
            self.signal_manager.process_new_game_data(game_data)
            
            # Actualizar estadísticas
            self._update_statistics()
            
        except Exception as e:
            logger.error(f"Error procesando para señales: {e}")
    
    async def _periodic_reports_loop(self):
        """Bucle de reportes periódicos"""
        report_interval = self.config.get('report_interval_minutes', 30) * 60
        
        while self.running:
            try:
                # Esperar intervalo de reporte
                await asyncio.sleep(report_interval)
                
                # Generar y enviar reporte
                await self._send_status_report()
                
            except Exception as e:
                logger.error(f"Error en reportes periódicos: {e}")
    
    async def _send_status_report(self):
        """Envía reporte de estado"""
        try:
            # Obtener estadísticas
            signal_stats = self.signal_manager.get_signal_statistics()
            data_stats = self.data_aggregator.get_statistics()
            
            # Calcular tiempo de operación
            if self.stats['start_time']:
                uptime = datetime.now() - self.stats['start_time']
                uptime_str = f"{uptime.total_seconds()/3600:.1f}h"
            else:
                uptime_str = "0h"
            
            # Crear mensaje de reporte
            report_msg = f"""
📊 *REPORTE DE ESTADO - BACCARAT SIGNALS*

⏱️ *Tiempo de operación:* {uptime_str}
🎯 *Señales enviadas:* {self.stats['signals_sent']}
🟢 *Alta confianza:* {self.stats['high_confidence_signals']}
📈 *Beneficio:* ${self.stats['total_profit']:+.2f}
🎲 *Acierto:* {self.stats['success_rate']:.1%}

🏦 *Datos procesados:* {data_stats.get('total_hands', 0)} manos
📊 *Mesas activas:* {data_stats.get('tables_played', 0)}
🎲 *Distribución:*
   • Banker: {data_stats.get('banker_percentage', 0):.1%}
   • Player: {data_stats.get('player_percentage', 0):.1%}
   • Tie: {data_stats.get('tie_percentage', 0):.1%}

🚀 *Sistema operativo*
💰 *Listo para próximas señales*
            """
            
            await self.telegram_bot.send_message(report_msg)
            
        except Exception as e:
            logger.error(f"Error enviando reporte: {e}")
    
    def _update_statistics(self):
        """Actualiza estadísticas del bot"""
        try:
            # Actualizar contadores básicos
            signal_stats = self.signal_manager.get_signal_statistics()
            
            self.stats['signals_sent'] = signal_stats.get('total_signals', 0)
            self.stats['high_confidence_signals'] = signal_stats.get('high_confidence_signals', 0)
            
        except Exception as e:
            logger.error(f"Error actualizando estadísticas: {e}")
    
    def _save_stats(self):
        """Guarda estadísticas finales"""
        try:
            stats_data = {
                'final_stats': self.stats,
                'end_time': datetime.now().isoformat(),
                'signal_history': self.signal_manager.signal_history[-100:]  # Últimas 100 señales
            }
            
            filename = f"telegram_signals_stats_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w') as f:
                json.dump(stats_data, f, indent=2, default=str)
                
            logger.info(f"Estadísticas guardadas en: {filename}")
            
        except Exception as e:
            logger.error(f"Error guardando estadísticas: {e}")


class SignalFormatter:
    """Formateador especializado de señales para Telegram"""
    
    @staticmethod
    def format_signal_message(signal: Signal) -> str:
        """Formatea señal para Telegram con estilo mejorado"""
        
        # Emojis por confianza
        confidence_emojis = {
            'HIGH': '🟢🔥',
            'MEDIUM': '🟡⚡',
            'LOW': '🔴💤'
        }
        
        # Emojis por tipo de apuesta
        bet_emojis = {
            'B': '🏦💰',
            'P': '👤💵',
            'T': '🤝💎'
        }
        
        # Colores para probabilidades
        def get_prob_color(prob):
            if prob > 0.5:
                return f"*{prob:.1%}*"  # Negrita para alta probabilidad
            else:
                return f"_{prob:.1%}_"  # Cursiva para baja probabilidad
        
        message = f"""
🎯 *NUEVA SEÑAL BACCARAT* 🎯

{confidence_emojis.get(signal.confidence.value, '⚪')} *CONFIANZA:* {signal.confidence.value} ({signal.confidence_score:.1%})

{bet_emojis.get(signal.recommended_bet, '🎲')} *APUESTA:* **{signal.recommended_bet}**
💰 *CANTIDAD:* {signal.bet_size} unidades
📊 *VALOR ESPERADO:* {signal.expected_value:+.2f}
⚠️ *RIESGO:* {signal.risk_level}

📈 *PROBABILIDADES:*
   🏦 Banker: {get_prob_color(signal.monte_carlo_probs.get('B', 0))}
   👤 Player: {get_prob_color(signal.monte_carlo_probs.get('P', 0))}
   🤝 Tie: {get_prob_color(signal.monte_carlo_probs.get('T', 0))}

🧠 *ANÁLISIS:*
   • Factor principal: {signal.reasoning.get('primary_factor', 'estadístico')}
   • Fuerza patrón: {signal.pattern_analysis.get('pattern_strength', 0):.2f}
   • Fuentes confianza: {len(signal.reasoning.get('confidence_sources', []))}

⏰ *Tiempo:* {signal.timestamp.strftime('%H:%M:%S')}
🆔 *Mesa:* {signal.table_id}

🚀 *¡LISTO PARA APOSTAR!*
        """
        
        return message.strip()
    
    @staticmethod
    def format_quick_signal(bet_type: str, confidence: str, bet_size: int) -> str:
        """Formatea señal rápida para decisiones inmediatas"""
        
        emojis = {
            'B': '🏦',
            'P': '👤',
            'T': '🤝'
        }
        
        confidence_symbols = {
            'HIGH': '🔥',
            'MEDIUM': '⚡',
            'LOW': '💤'
        }
        
        return f"""
🎯 {emojis.get(bet_type, '🎲')} *{bet_type}* {confidence_symbols.get(confidence, '')} *{confidence}*
💰 {bet_size}u
        """.strip()


def load_telegram_config() -> Dict:
    """Carga configuración para bot de Telegram"""
    return {
        'telegram': {
            'bot_token': 'YOUR_BOT_TOKEN_HERE',
            'chat_id': 'YOUR_CHAT_ID_HERE'
        },
        'data_sources': [
            {
                'enabled': True,
                'casino_name': 'evolution_gaming',
                'api_key': 'YOUR_API_KEY_HERE'
            }
        ],
        'report_interval_minutes': 30,
        'min_confidence': 'MEDIUM',
        'max_signals_per_hour': 10
    }


async def main():
    """Función principal para bot de Telegram"""
    try:
        # Cargar configuración
        config = load_telegram_config()
        
        # Crear bot
        bot = TelegramSignalsBot(config)
        
        # Inicializar
        await bot.initialize()
        
        # Iniciar
        await bot.start()
        
    except Exception as e:
        logger.error(f"Error en bot de Telegram: {e}")


if __name__ == "__main__":
    asyncio.run(main())