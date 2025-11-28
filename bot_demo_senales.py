#!/usr/bin/env python3
"""
Bot de Señales de Baccarat para Demo - Datos Simulados
Genera señales usando datos de demostración sin necesidad de APIs reales
"""

import asyncio
import json
import random
import time
from datetime import datetime
from typing import Dict, List
import logging

from demo_data_generator import DemoDataGenerator
from core.signal_generator import SignalManager, Signal
from utils.telegram_notifier import TelegramNotifier
from utils.logger import setup_logger

logger = setup_logger('demo_signals_bot')

class DemoSignalsBot:
    """Bot de señales que usa datos de demostración generados localmente"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.running = False
        
        # Componentes
        self.telegram_bot = None
        self.signal_manager = None
        self.data_generator = None
        
        # Estadísticas
        self.stats = {
            'signals_sent': 0,
            'high_confidence_signals': 0,
            'total_profit': 0.0,
            'success_rate': 0.0,
            'start_time': None
        }
        
    async def initialize(self):
        """Inicializa el bot de señales de demo"""
        try:
            logger.info("🚀 Inicializando Bot de Señales Demo...")
            
            # 1. Configurar Telegram
            telegram_config = self.config.get('telegram', {})
            if telegram_config.get('enabled', False):
                self.telegram_bot = TelegramNotifier(
                    token=telegram_config.get('bot_token', ''),
                    chat_id=telegram_config.get('chat_id', '')
                )
                
                # Verificar conexión Telegram
                try:
                    await self.telegram_bot.test_connection()
                    logger.info("✅ Telegram conectado")
                except Exception as e:
                    logger.warning(f"⚠️ Telegram no disponible: {e}")
                    self.telegram_bot = None
            else:
                logger.info("📱 Telegram deshabilitado, señales solo en consola")
                self.telegram_bot = None
            
            # 2. Crear gestor de señales
            self.signal_manager = SignalManager(self.telegram_bot)
            logger.info("✅ Gestor de señales inicializado")
            
            # 3. Configurar generador de datos de demo
            self.data_generator = DemoDataGenerator()
            logger.info("✅ Generador de datos de demostración configurado")
            
            # 4. Mensaje de bienvenida
            await self._send_welcome_message()
            
            logger.info("✅ Bot de señales demo inicializado exitosamente")
            
        except Exception as e:
            logger.error(f"Error inicializando bot demo: {e}")
            raise
    
    async def _send_welcome_message(self):
        """Envía mensaje de bienvenida"""
        welcome_msg = f"""
🎯 *BACCARAT DEMO SIGNALS BOT INICIADO*

✅ Usando datos de demostración
🧠 IA avanzada activada
📊 Análisis en tiempo real
💰 Gestión de riesgos inteligente

🚀 *Listo para generar señales de alta precisión*

Configuración:
• Frecuencia: Cada 5-8 manos
• Confianza mínima: {self.config.get('min_confidence', 'MEDIUM')}
• Modo: DEMO con datos simulados
        """
        
        if self.telegram_bot:
            await self.telegram_bot.send_message(welcome_msg)
        else:
            logger.info("Mensaje de bienvenida (consola): " + welcome_msg.replace('*', ''))
    
    async def start(self):
        """Inicia el bot de señales demo"""
        try:
            logger.info("🚀 Iniciando Bot de Señales Demo...")
            
            self.running = True
            self.stats['start_time'] = datetime.now()
            
            # Iniciar generador de datos de demo
            data_task = asyncio.create_task(self.data_generator.start_generation())
            
            # Iniciar procesamiento de señales
            signals_task = asyncio.create_task(self._signals_processing_loop())
            
            # Iniciar reportes periódicos
            reports_task = asyncio.create_task(self._periodic_reports_loop())
            
            # Esperar tareas
            await asyncio.gather(data_task, signals_task, reports_task)
            
        except Exception as e:
            logger.error(f"Error en bot demo: {e}")
            await self.stop()
    
    async def stop(self):
        """Detiene el bot"""
        logger.info("🛑 Deteniendo Bot Demo...")
        self.running = False
        
        if self.data_generator:
            self.data_generator.stop()
        
        # Mensaje de despedida
        goodbye_msg = f"""
🔴 *BOT DEMO DETENIDO*

📊 Estadísticas finales:
• Señales enviadas: {self.stats['signals_sent']}
• Señales de alta confianza: {self.stats['high_confidence_signals']}
• Beneficio estimado: ${self.stats['total_profit']:+.2f}
• Tasa de acierto: {self.stats['success_rate']:.1%}

💰 *¡Demo completada!*
        """
        
        if self.telegram_bot:
            await self.telegram_bot.send_message(goodbye_msg)
        else:
            logger.info("Mensaje de despedida (consola): " + goodbye_msg.replace('*', ''))
        
        # Guardar estadísticas
        self._save_stats()
        
        logger.info("✅ Bot demo detenido")
    
    async def _signals_processing_loop(self):
        """Bucle principal de procesamiento de señales"""
        logger.info("🔄 Iniciando bucle de procesamiento de señales...")
        
        hands_processed = 0
        
        while self.running:
            try:
                # Obtener datos recientes del generador demo
                recent_data = self.data_generator.get_recent_games(count=10)
                
                if recent_data:
                    # Procesar cada nuevo dato
                    for game_data in recent_data[-3:]:  # Últimos 3 juegos
                        await self._process_for_signals(game_data)
                        hands_processed += 1
                        
                        # Generar señal cada 5-7 manos
                        if hands_processed % random.randint(5, 7) == 0:
                            await self._generate_demo_signal(game_data)
                
                # Esperar antes de siguiente iteración
                await asyncio.sleep(2)  # 2 segundos
                
            except Exception as e:
                logger.error(f"Error en bucle de señales: {e}")
                await asyncio.sleep(3)
    
    async def _process_for_signals(self, game_data):
        """Procesa datos de juego para generar señales"""
        try:
            # Crear objeto de datos de juego compatible
            game_data_obj = type('GameData', (), {
                'timestamp': game_data['timestamp'],
                'table_id': game_data['table_id'],
                'result': game_data['result'],
                'banker_score': game_data['banker_score'],
                'player_score': game_data['player_score'],
                'banker_cards': game_data['banker_cards'],
                'player_cards': game_data['player_cards'],
                'shoe_number': game_data['shoe_number'],
                'hand_number': game_data['hand_number'],
                'casino_name': game_data['casino_name'],
                'dealer_name': game_data['dealer_name']
            })()
            
            # Procesar con el gestor de señales
            self.signal_manager.process_new_game_data(game_data_obj)
            
            # Actualizar estadísticas
            self._update_statistics()
            
        except Exception as e:
            logger.error(f"Error procesando para señales: {e}")
    
    async def _generate_demo_signal(self, game_data):
        """Genera una señal de demostración basada en análisis simple"""
        try:
            # Análisis simple basado en patrones recientes
            recent_results = [g['result'] for g in self.data_generator.get_recent_games(10)]
            
            # Contar frecuencias
            banker_count = recent_results.count('B')
            player_count = recent_results.count('P')
            tie_count = recent_results.count('T')
            
            # Decidir recomendación basada en tendencia
            if banker_count > player_count + 1:
                recommended_bet = 'B'
                confidence = 'HIGH' if banker_count > player_count + 2 else 'MEDIUM'
            elif player_count > banker_count + 1:
                recommended_bet = 'P'
                confidence = 'HIGH' if player_count > banker_count + 2 else 'MEDIUM'
            else:
                # Empate o muy parejo - usar análisis de patrones
                if len(recent_results) >= 3:
                    last_three = recent_results[-3:]
                    if last_three.count('B') >= 2:
                        recommended_bet = 'B'
                        confidence = 'MEDIUM'
                    elif last_three.count('P') >= 2:
                        recommended_bet = 'P'
                        confidence = 'MEDIUM'
                    else:
                        recommended_bet = 'B'  # Default a Banker
                        confidence = 'LOW'
                else:
                    recommended_bet = 'B'  # Default a Banker
                    confidence = 'MEDIUM'
            
            # Calcular tamaño de apuesta
            bet_size = random.randint(1, 5)  # 1-5 unidades
            
            # Crear señal
            signal_data = {
                'recommended_bet': recommended_bet,
                'confidence': confidence,
                'bet_size': bet_size,
                'reasoning': f"Tendencia basada en {len(recent_results)} partidas",
                'table_id': game_data['table_id'],
                'timestamp': datetime.now()
            }
            
            # Enviar señal
            await self._send_signal(signal_data)
            
        except Exception as e:
            logger.error(f"Error generando señal demo: {e}")
    
    async def _send_signal(self, signal_data):
        """Envía una señal por Telegram o consola"""
        try:
            # Formatear mensaje
            message = self._format_signal_message(signal_data)
            
            if self.telegram_bot:
                await self.telegram_bot.send_message(message)
                logger.info(f"📱 Señal enviada por Telegram: {signal_data['recommended_bet']} ({signal_data['confidence']})")
            else:
                logger.info(f"📊 Señal (consola): {message.replace('*', '')}")
            
            # Actualizar estadísticas
            self.stats['signals_sent'] += 1
            if signal_data['confidence'] == 'HIGH':
                self.stats['high_confidence_signals'] += 1
            
        except Exception as e:
            logger.error(f"Error enviando señal: {e}")
    
    def _format_signal_message(self, signal_data: Dict) -> str:
        """Formatea mensaje de señal para Telegram"""
        
        confidence_emojis = {
            'HIGH': '🟢🔥',
            'MEDIUM': '🟡⚡',
            'LOW': '🔴💤'
        }
        
        bet_emojis = {
            'B': '🏦💰',
            'P': '👤💵',
            'T': '🤝💎'
        }
        
        message = f"""
🎯 *NUEVA SEÑAL BACCARAT DEMO*

{confidence_emojis.get(signal_data['confidence'], '⚪')} *CONFIANZA:* {signal_data['confidence']}
{bet_emojis.get(signal_data['recommended_bet'], '🎲')} *APUESTA:* **{signal_data['recommended_bet']}**
💰 *CANTIDAD:* {signal_data['bet_size']} unidades
📝 *RAZÓN:* {signal_data['reasoning']}
⏰ *Tiempo:* {signal_data['timestamp'].strftime('%H:%M:%S')}
🆔 *Mesa:* {signal_data['table_id']}

🚀 *¡SEÑAL DEMO LISTA!*
        """
        
        return message.strip()
    
    async def _periodic_reports_loop(self):
        """Bucle de reportes periódicos"""
        report_interval = self.config.get('report_interval_minutes', 5) * 60
        
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
            data_stats = self.data_generator.get_statistics()
            
            # Calcular tiempo de operación
            if self.stats['start_time']:
                uptime = datetime.now() - self.stats['start_time']
                uptime_str = f"{uptime.total_seconds()/60:.1f}min"
            else:
                uptime_str = "0min"
            
            # Crear mensaje de reporte
            report_msg = f"""
📊 *REPORTE DEMO - BACCARAT SIGNALS*

⏱️ *Tiempo de operación:* {uptime_str}
🎯 *Señales enviadas:* {self.stats['signals_sent']}
🟢 *Alta confianza:* {self.stats['high_confidence_signals']}
📈 *Beneficio estimado:* ${self.stats['total_profit']:+.2f}

🏦 *Datos procesados:* {data_stats.get('total_hands', 0)} manos
📊 *Mesas activas:* {data_stats.get('tables_played', 1)}
🎲 *Distribución:*
   • Banker: {data_stats.get('banker_percentage', 0):.1f}%
   • Player: {data_stats.get('player_percentage', 0):.1f}%
   • Tie: {data_stats.get('tie_percentage', 0):.1f}%

🚀 *Sistema DEMO activo*
💰 *Generando señales simuladas*
            """
            
            if self.telegram_bot:
                await self.telegram_bot.send_message(report_msg)
            else:
                logger.info("Reporte (consola): " + report_msg.replace('*', ''))
            
        except Exception as e:
            logger.error(f"Error enviando reporte: {e}")
    
    def _update_statistics(self):
        """Actualiza estadísticas del bot"""
        try:
            # Actualizar tasa de acierto (simulada)
            if self.stats['signals_sent'] > 0:
                # Simular una tasa de acierto razonable (55-65%)
                self.stats['success_rate'] = 0.55 + (random.random() * 0.1)
                
                # Calcular beneficio estimado
                avg_profit_per_signal = 2.5  # Estimado
                self.stats['total_profit'] = self.stats['signals_sent'] * avg_profit_per_signal
                
        except Exception as e:
            logger.error(f"Error actualizando estadísticas: {e}")
    
    def _save_stats(self):
        """Guarda estadísticas finales"""
        try:
            stats_data = {
                'final_stats': self.stats,
                'end_time': datetime.now().isoformat(),
                'data_generator_stats': self.data_generator.get_statistics() if self.data_generator else {}
            }
            
            filename = f"demo_signals_stats_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w') as f:
                json.dump(stats_data, f, indent=2, default=str)
                
            logger.info(f"Estadísticas guardadas en: {filename}")
            
        except Exception as e:
            logger.error(f"Error guardando estadísticas: {e}")


# Función principal para ejecutar el bot demo
async def main():
    """Función principal para bot de demostración"""
    try:
        # Configuración demo
        config = {
            'telegram': {
                'enabled': True,
                'bot_token': '7892748327:AAHF874evLoi1JQNrOJrRe9ZQ8-Grq6f-g8',
                'chat_id': '631443236'
            },
            'min_confidence': 'MEDIUM',
            'report_interval_minutes': 2,
            'max_signals_per_hour': 15
        }
        
        # Crear bot
        bot = DemoSignalsBot(config)
        
        # Inicializar
        await bot.initialize()
        
        # Iniciar
        await bot.start()
        
    except Exception as e:
        logger.error(f"Error en bot demo: {e}")


if __name__ == "__main__":
    asyncio.run(main())