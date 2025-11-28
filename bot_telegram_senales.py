#!/usr/bin/env python3
"""
Bot que envía señales directamente a Telegram
"""

import time
import random
from datetime import datetime
from utils.telegram_notifier import telegram_notifier
from utils.logger import logger

def generar_senal_telegram(historial):
    """Genera señal y la envía a Telegram"""
    
    if len(historial) < 3:
        mensaje = """
⚠️ <b>ESPERANDO DATOS</b>

📊 Se necesitan al menos 3 resultados para generar señales
⏰ El bot continuará capturando datos...
        """
        telegram_notifier.send_message(mensaje)
        return "ESPERANDO_DATOS", 0.0
    
    # Análisis simple
    ultimos_3 = historial[-3:]
    b_count = ultimos_3.count('B')
    p_count = ultimos_3.count('P')
    
    # Generar señal
    if b_count >= 2:
        senal = 'B'
        confianza = 0.6
        emoji = "🎯"
        color = "🔴"
        nombre = "DRAGON"
    elif p_count >= 2:
        senal = 'P'
        confianza = 0.6
        emoji = "🎯"
        color = "🔵"
        nombre = "TIGER"
    else:
        senal = 'NONE'
        confianza = 0.0
        emoji = "⚡"
        color = "⚪"
        nombre = "SIN TENDENCIA"
    
    # Enviar a Telegram
    if senal != 'NONE':
        mensaje = f"""
{emoji} <b>SEÑAL DE APOSTAR - BACCARAT</b>

🎮 <b>Juego:</b> Lightning Dragon Tiger
{color} <b>Señal:</b> {nombre} ({senal})
📊 <b>Confianza:</b> {confianza*100:.0f}%
📈 <b>Análisis:</b> {b_count} Dragon vs {p_count} Tiger en últimos 3

💰 <b>Recomendación:</b> Apostar ${confianza:.1f} a {nombre}
⏰ <b>Hora:</b> {datetime.now().strftime('%H:%M:%S')}
        """
    else:
        mensaje = f"""
⚡ <b>SEÑAL NEUTRA</b>

📊 Últimos 3: {ultimos_3}
🧠 Análisis: Sin patrón claro detectado
💰 Recomendación: No apostar en este momento
⏰ Hora: {datetime.now().strftime('%H:%M:%S')}
        """
    
    # Enviar a Telegram
    success = telegram_notifier.send_message(mensaje)
    if success:
        print(f"✅ Señal enviada a Telegram: {senal} con confianza {confianza}")
    else:
        print("❌ Error al enviar a Telegram")
    
    return senal, confianza

def main():
    """Bot principal que envía señales a Telegram"""
    
    print("🚀 BOT DE SEÑALES PARA TELEGRAM")
    print("="*50)
    print("Enviando señales cada 10 segundos...")
    print("="*50)
    
    # Probar conexión con Telegram
    print("🔍 Probando conexión con Telegram...")
    if telegram_notifier.test_connection():
        print("✅ Conexión exitosa con Telegram")
    else:
        print("❌ Error conectando a Telegram - verifica token y chat_id")
        return
    
    # Mensaje inicial
    mensaje_inicio = """
🤖 <b>BOT DE SEÑALES BACCARAT INICIADO</b>

✅ El bot está activo y generará señales
⏰ Actualización cada 10 segundos
🎯 Señales basadas en análisis de tendencia

¡Comenzando captura de datos!
    """
    telegram_notifier.send_message(mensaje_inicio)
    
    historial = ['B', 'P', 'B', 'B', 'P']  # Datos iniciales
    iteracion = 0
    
    try:
        while True:
            iteracion += 1
            print(f"\n--- ITERACIÓN {iteracion} ---")
            
            # Agregar nuevo resultado
            nuevo = random.choice(['B', 'P', 'B', 'P', 'B'])
            historial.append(nuevo)
            
            print(f"📊 Datos: {len(historial)} resultados")
            print(f"Últimos 5: {historial[-5:]}")
            
            # Generar y enviar señal
            senal, confianza = generar_senal_telegram(historial)
            
            # Mantener solo últimos 50 resultados
            if len(historial) > 50:
                historial = historial[-50:]
            
            print(f"⏰ Esperando 10 segundos...")
            time.sleep(10)
            
    except KeyboardInterrupt:
        print("\n⏹️ Bot detenido por el usuario")
        
        mensaje_final = """
🛑 <b>BOT DETENIDO</b>

👤 El bot fue detenido manualmente
📊 Total de señales generadas: """ + str(iteracion) + """
✅ Gracias por usar el sistema de señales
        """
        telegram_notifier.send_message(mensaje_final)

if __name__ == "__main__":
    main()