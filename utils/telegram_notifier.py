# utils/telegram_notifier.py
import requests
from typing import Optional, Dict, Any
from config.settings import settings
from utils.logger import logger


class TelegramNotifier:
    """Manejador de notificaciones de Telegram"""
    
    def __init__(self):
        self.token = settings.telegram.bot_token
        self.chat_id = settings.telegram.chat_id
        self.enabled = settings.telegram.enabled
        self.base_url = f"https://api.telegram.org/bot{self.token}"
        
    def send_message(self, message: str, parse_mode: str = "HTML") -> bool:
        """
        Enviar mensaje a Telegram
        
        Args:
            message: Texto del mensaje
            parse_mode: Formato del mensaje (HTML, Markdown, etc.)
            
        Returns:
            bool: True si se envió correctamente, False en caso contrario
        """
        if not self.enabled:
            logger.debug("Telegram deshabilitado, mensaje no enviado")
            return False
            
        try:
            url = f"{self.base_url}/sendMessage"
            payload = {
                "chat_id": self.chat_id,
                "text": message,
                "parse_mode": parse_mode
            }
            
            response = requests.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                logger.info(f"Mensaje enviado a Telegram: {message[:50]}...")
                return True
            else:
                logger.error(f"Error al enviar mensaje a Telegram: "
                             f"{response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Excepción al enviar mensaje a Telegram: {e}")
            return False
    
    def send_prediction_signal(self, game_type: str, prediction: str,
                               confidence: float, reasoning: str = "",
                               additional_info: Optional[Dict[str, Any]] = None
                               ) -> bool:
        """
        Enviar señal de predicción formateada
        
        Args:
            game_type: Tipo de juego (Dragon, Tiger, Tie)
            prediction: Predicción (Dragon, Tiger, Tie)
            confidence: Nivel de confianza (0-100)
            reasoning: Razón de la predicción
            additional_info: Información adicional
            
        Returns:
            bool: True si se envió correctamente
        """
        emoji = "🎯" if confidence > 70 else "⚡" if confidence > 50 else "🎲"
        
        message = f"""
{emoji} <b>SEÑAL DE PREDICCIÓN - LIGHTNING DRAGON TIGER</b>

🎮 <b>Juego:</b> {game_type}
🔮 <b>Predicción:</b> {prediction}
📊 <b>Confianza:</b> {confidence:.1f}%

"""
        
        if reasoning:
            message += f"🧠 <b>Análisis:</b> {reasoning}\n\n"
        
        if additional_info:
            message += "📈 <b>Estadísticas:</b>\n"
            for key, value in additional_info.items():
                message += f"• {key}: {value}\n"
        
        message += "\n<i>¡Buena suerte!</i>"
        
        return self.send_message(message.strip())
    
    def send_result_notification(self, prediction: str, result: str,
                                 won: bool, profit: float, balance: float
                                 ) -> bool:
        """
        Enviar notificación de resultado de apuesta
        
        Args:
            prediction: Predicción realizada
            result: Resultado real
            won: Si se ganó o perdió
            profit: Ganancia/perdida
            balance: Balance actual
            
        Returns:
            bool: True si se envió correctamente
        """
        emoji = "✅" if won else "❌"
        profit_emoji = "💰" if profit > 0 else "📉"
        
        message = f"""
{emoji} <b>RESULTADO DE APUESTA</b>

🔮 <b>Predicción:</b> {prediction}
🎯 <b>Resultado:</b> {result}
{profit_emoji} <b>Ganancia:</b> ${profit:.2f}
💳 <b>Balance:</b> ${balance:.2f}
"""
        
        return self.send_message(message.strip())
    
    def send_error_notification(self, error_type: str, error_message: str,
                                context: Optional[str] = None) -> bool:
        """
        Enviar notificación de error
        
        Args:
            error_type: Tipo de error
            error_message: Mensaje de error
            context: Contexto adicional
            
        Returns:
            bool: True si se envió correctamente
        """
        message = f"""
⚠️ <b>ERROR DETECTADO</b>

🔥 <b>Tipo:</b> {error_type}
❗ <b>Mensaje:</b> {error_message}
"""
        
        if context:
            message += f"\n📝 <b>Contexto:</b> {context}"
        
        return self.send_message(message)
    
    def test_connection(self) -> bool:
        """
        Probar la conexión con Telegram
        
        Returns:
            bool: True si la conexión es exitosa
        """
        try:
            url = f"{self.base_url}/getMe"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("ok"):
                    bot_info = data.get("result", {})
                    logger.info(f"Conexión exitosa con bot: "
                                f"@{bot_info.get('username', 'unknown')}")
                    return True
                else:
                    logger.error("La API respondió pero no está OK")
                    return False
            else:
                logger.error(f"Error al conectar con Telegram: "
                             f"{response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Excepción al probar conexión: {e}")
            return False


# Instancia global del notificador
telegram_notifier = TelegramNotifier()