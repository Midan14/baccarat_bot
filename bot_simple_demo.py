#!/usr/bin/env python3
"""
Bot Simple de Demostración - Genera señales básicas de Baccarat
Versión simplificada para demostrar el funcionamiento
"""

import asyncio
import random
import time
from datetime import datetime

# Configuración de Telegram (usar valores del .env)
TELEGRAM_BOT_TOKEN = "7892748327:AAHF874evLoi1JQNrOJrRe9ZQ8-Grq6f-g8"
TELEGRAM_CHAT_ID = "631443236"

class SimpleDemoBot:
    """Bot simple que genera señales de demostración"""
    
    def __init__(self):
        self.running = False
        self.signals_sent = 0
        self.start_time = None
        
    async def start(self):
        """Inicia el bot"""
        print("🚀 Iniciando Bot Demo Simple...")
        self.running = True
        self.start_time = datetime.now()
        
        while self.running:
            try:
                # Generar señal cada 10-15 segundos
                await self.generate_signal()
                await asyncio.sleep(random.randint(10, 15))
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                await asyncio.sleep(5)
    
    async def generate_signal(self):
        """Genera una señal simple"""
        # Decidir apuesta basada en probabilidades
        rand = random.random()
        if rand < 0.45:
            bet = 'B'  # Banker
            confidence = 'HIGH' if rand < 0.15 else 'MEDIUM'
        elif rand < 0.90:
            bet = 'P'  # Player
            confidence = 'HIGH' if rand > 0.75 else 'MEDIUM'
        else:
            bet = 'T'  # Tie
            confidence = 'LOW'
        
        # Tamaño de apuesta
        bet_size = random.randint(1, 5)
        
        # Crear mensaje
        message = self.format_message(bet, confidence, bet_size)
        
        # Enviar señal
        await self.send_signal(message, bet, confidence, bet_size)
        
        # Actualizar contador
        self.signals_sent += 1
    
    def format_message(self, bet, confidence, bet_size):
        """Formatea el mensaje de la señal"""
        emojis = {
            'B': '🏦💰',
            'P': '👤💵', 
            'T': '🤝💎'
        }
        
        confidence_emojis = {
            'HIGH': '🟢🔥',
            'MEDIUM': '🟡⚡',
            'LOW': '🔴💤'
        }
        
        return f"""
🎯 *NUEVA SEÑAL BACCARAT*

{confidence_emojis.get(confidence, '⚪')} *CONFIANZA:* {confidence}
{emojis.get(bet, '🎲')} *APUESTA:* **{bet}**
💰 *CANTIDAD:* {bet_size} unidades
⏰ *Tiempo:* {datetime.now().strftime('%H:%M:%S')}

🚀 *¡LISTO PARA APOSTAR!*
        """.strip()
    
    async def send_signal(self, message, bet, confidence, bet_size):
        """Envía la señal por Telegram o consola"""
        try:
            # Intentar enviar por Telegram
            import requests
            
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
            params = {
                'chat_id': TELEGRAM_CHAT_ID,
                'text': message,
                'parse_mode': 'Markdown'
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                print(f"✅ Señal enviada por Telegram: {bet} ({confidence}) - {bet_size}u")
            else:
                print(f"⚠️ Telegram error {response.status_code}: {response.text}")
                # Mostrar en consola como backup
                print(f"📊 Señal (consola): {bet} ({confidence}) - {bet_size}u")
                
        except Exception as e:
            print(f"📊 Señal (consola): {bet} ({confidence}) - {bet_size}u")
            print(f"   Mensaje: {message.replace('*', '')}")
    
    def stop(self):
        """Detiene el bot"""
        self.running = False
        runtime = datetime.now() - self.start_time if self.start_time else 0
        print(f"""
🛑 Bot detenido
⏱️ Tiempo de ejecución: {runtime}
📊 Señales generadas: {self.signals_sent}
        """)


async def main():
    """Función principal"""
    bot = SimpleDemoBot()
    
    print("🎮 Bot Demo Simple iniciado")
    print("Presiona Ctrl+C para detener")
    
    try:
        await bot.start()
    except KeyboardInterrupt:
        print("\n🛑 Deteniendo bot...")
        bot.stop()


if __name__ == "__main__":
    asyncio.run(main())