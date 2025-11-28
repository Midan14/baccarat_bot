"""
Notificador de Telegram para señales y reportes
"""

import asyncio
import aiohttp
from typing import Dict, List, Optional
import json
import time
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class TelegramNotifier:
    """Gestiona notificaciones a través de Telegram"""
    
    def __init__(self, token: str, chat_id: str, admin_chat_id: str = None):
        self.token = token
        self.chat_id = chat_id
        self.admin_chat_id = admin_chat_id or chat_id
        self.base_url = f"https://api.telegram.org/bot{token}"
        self.session = None
        
        # Estadísticas
        self.messages_sent = 0
        self.errors_count = 0
        self.last_error = None
        
    async def initialize(self):
        """Inicializa la conexión"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30)
        )
        
        # Verificar conexión
        await self.test_connection()
    
    async def test_connection(self) -> bool:
        """Verifica que el bot está funcionando"""
        try:
            async with self.session.get(f"{self.base_url}/getMe") as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('ok'):
                        bot_info = data.get('result', {})
                        logger.info(f"✅ Bot conectado: {bot_info.get('first_name', 'Unknown')}")
                        return True
                    else:
                        logger.error(f"Error en respuesta de Telegram: {data}")
                        return False
                else:
                    logger.error(f"Error HTTP: {response.status}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error conectando a Telegram: {e}")
            return False
    
    async def send_message(self, message: str, parse_mode: str = "HTML", disable_notification: bool = False) -> bool:
        """Envía un mensaje a Telegram"""
        try:
            if not self.session:
                await self.initialize()
            
            payload = {
                'chat_id': self.chat_id,
                'text': message,
                'parse_mode': parse_mode,
                'disable_notification': disable_notification
            }
            
            # Limitar longitud del mensaje
            if len(message) > 4096:
                message = message[:4093] + "..."
                payload['text'] = message
            
            async with self.session.post(
                f"{self.base_url}/sendMessage",
                json=payload
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    if result.get('ok'):
                        self.messages_sent += 1
                        logger.debug("Mensaje enviado exitosamente")
                        return True
                    else:
                        logger.error(f"Error en respuesta: {result}")
                        self.errors_count += 1
                        return False
                else:
                    logger.error(f"Error HTTP: {response.status}")
                    self.errors_count += 1
                    return False
                    
        except Exception as e:
            logger.error(f"Error enviando mensaje: {e}")
            self.errors_count += 1
            self.last_error = str(e)
            return False
    
    async def send_signal(self, signal_data: Dict) -> bool:
        """Envía una señal formateada"""
        
        message = self._format_signal_message(signal_data)
        return await self.send_message(message)
    
    async def send_report(self, report_data: Dict) -> bool:
        """Envía un reporte formateado"""
        
        message = self._format_report_message(report_data)
        return await self.send_message(message)
    
    async def send_alert(self, alert_type: str, message: str) -> bool:
        """Envía una alerta de administrador"""
        
        alert_message = f"""
    🚨 <b>ALERTA ADMINISTRADOR</b> 🚨

    <b>Tipo:</b> {alert_type.upper()}
    <b>Mensaje:</b> {message}
    <b>Tiempo:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        
        # Enviar al chat de administrador
        original_chat_id = self.chat_id
        self.chat_id = self.admin_chat_id
        
        try:
            result = await self.send_message(alert_message)
            return result
        finally:
            self.chat_id = original_chat_id
    
    async def send_photo(self, photo_path: str, caption: str = "", 
                        parse_mode: str = "HTML") -> bool:
        """Envía una foto"""
        try:
            if not self.session:
                await self.initialize()
            
            with open(photo_path, 'rb') as photo_file:
                form_data = aiohttp.FormData()
                form_data.add_field('chat_id', self.chat_id)
                form_data.add_field('photo', photo_file)
                form_data.add_field('caption', caption)
                form_data.add_field('parse_mode', parse_mode)
                
                async with self.session.post(
                    f"{self.base_url}/sendPhoto",
                    data=form_data
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result.get('ok', False)
                    else:
                        logger.error(f"Error HTTP enviando foto: {response.status}")
                        return False
                        
        except Exception as e:
            logger.error(f"Error enviando foto: {e}")
            return False
    
    async def send_document(self, document_path: str, caption: str = "") -> bool:
        """Envía un documento"""
        try:
            if not self.session:
                await self.initialize()
            
            with open(document_path, 'rb') as document_file:
                form_data = aiohttp.FormData()
                form_data.add_field('chat_id', self.chat_id)
                form_data.add_field('document', document_file)
                form_data.add_field('caption', caption)
                
                async with self.session.post(
                    f"{self.base_url}/sendDocument",
                    data=form_data
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result.get('ok', False)
                    else:
                        logger.error(f"Error HTTP enviando documento: {response.status}")
                        return False
                        
        except Exception as e:
            logger.error(f"Error enviando documento: {e}")
            return False
    
    def _format_signal_message(self, signal_data: Dict) -> str:
        """Formatea mensaje de señal"""
        
        confidence_emoji = {
            'HIGH': '🟢🔥',
            'MEDIUM': '🟡⚡',
            'LOW': '🔴💤'
        }
        
        bet_emoji = {
            'B': '🏦💰',
            'P': '👤💵',
            'T': '🤝💎'
        }
        
        # Probabilidades
        probs = signal_data.get('monte_carlo_probs', {})
        banker_prob = probs.get('B', 0)
        player_prob = probs.get('P', 0)
        tie_prob = probs.get('T', 0)
        
        message = f"""
    🎯 <b>NUEVA SEÑAL BACCARAT</b> 🎯

    {confidence_emoji.get(signal_data.get('confidence', ''), '⚪')} <b>CONFIANZA:</b> {signal_data.get('confidence', 'UNKNOWN')} ({signal_data.get('confidence_score', 0):.1%})

    {bet_emoji.get(signal_data.get('recommended_bet', ''), '🎲')} <b>APUESTA:</b> <b>{signal_data.get('recommended_bet', '?')}</b>
    💰 <b>CANTIDAD:</b> {signal_data.get('bet_size', 0)} unidades
    📊 <b>VALOR ESPERADO:</b> {signal_data.get('expected_value', 0):+.2f}
    ⚠️ <b>RIESGO:</b> {signal_data.get('risk_level', 'UNKNOWN')}

    📈 <b>PROBABILIDADES:</b>
       🏦 Banker: {banker_prob:.1%}
       👤 Player: {player_prob:.1%}
       🤝 Tie: {tie_prob:.1%}

    🧠 <b>ANÁLISIS:</b> {signal_data.get('reasoning', {}).get('primary_factor', 'estadístico')}
    ⏰ <b>Tiempo:</b> {signal_data.get('timestamp', datetime.now().isoformat())[:19]}
    🆔 <b>Mesa:</b> {signal_data.get('table_id', 'unknown')}

    🚀 <b>¡LISTO PARA APOSTAR!</b>
        """
        
        return message.strip()
    
    def _format_report_message(self, report_data: Dict) -> str:
        """Formatea mensaje de reporte"""
        
        message = f"""
    📊 <b>REPORTE DE ESTADO - BACCARAT BOT</b>

    ⏱️ <b>Tiempo de operación:</b> {report_data.get('uptime', '0h')}
    🎯 <b>Señales enviadas:</b> {report_data.get('signals_sent', 0)}
    🟢 <b>Alta confianza:</b> {report_data.get('high_confidence_signals', 0)}
    📈 <b>Beneficio:</b> ${report_data.get('total_profit', 0):+.2f}
    🎲 <b>Acierto:</b> {report_data.get('success_rate', 0):.1%}

    🏦 <b>Datos procesados:</b> {report_data.get('hands_processed', 0)} manos
    📊 <b>Mesas activas:</b> {report_data.get('active_tables', 0)}
    🎲 <b>Distribución:</b>
       • Banker: {report_data.get('banker_percentage', 0):.1%}
       • Player: {report_data.get('player_percentage', 0):.1%}
       • Tie: {report_data.get('tie_percentage', 0):.1%}

    🚀 <b>Sistema operativo</b>
    💰 <b>Listo para próximas señales</b>
        """
        
        return message.strip()
    
    async def close(self):
        """Cierra la conexión"""
        if self.session:
            await self.session.close()
    
    def get_stats(self) -> Dict:
        """Obtiene estadísticas"""
        return {
            'messages_sent': self.messages_sent,
            'errors_count': self.errors_count,
            'last_error': self.last_error,
            'success_rate': (self.messages_sent / (self.messages_sent + self.errors_count)) if (self.messages_sent + self.errors_count) > 0 else 0
        }


class TelegramBotManager:
    """Gestiona múltiples bots de Telegram"""
    
    def __init__(self):
        self.bots: Dict[str, TelegramNotifier] = {}
        self.default_bot = None
    
    def add_bot(self, name: str, token: str, chat_id: str, admin_chat_id: str = None):
        """Agrega un bot"""
        self.bots[name] = TelegramNotifier(token, chat_id, admin_chat_id)
        if not self.default_bot:
            self.default_bot = name
    
    def get_bot(self, name: str = None) -> Optional[TelegramNotifier]:
        """Obtiene un bot por nombre"""
        if name is None:
            name = self.default_bot
        return self.bots.get(name)
    
    async def initialize_all(self):
        """Inicializa todos los bots"""
        for bot in self.bots.values():
            await bot.initialize()
    
    async def send_to_all(self, message: str, parse_mode: str = "HTML"):
        """Envía mensaje a todos los bots"""
        tasks = []
        for bot in self.bots.values():
            task = bot.send_message(message, parse_mode)
            tasks.append(task)
        
        if tasks:
            await asyncio.gather(*tasks)
    
    def get_all_stats(self) -> Dict:
        """Obtiene estadísticas de todos los bots"""
        stats = {}
        for name, bot in self.bots.items():
            stats[name] = bot.get_stats()
        return stats