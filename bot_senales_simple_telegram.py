#!/usr/bin/env python3
"""
Bot simple con señales tempranas para Baccarat con integración real de Telegram
"""

import random
import asyncio
from datetime import datetime
from utils.telegram_notifier import TelegramNotifier
from config.settings import BotConfig


def generar_senal_temprana(historial):
    """Genera señales con muy pocos datos (3+)"""
    
    if len(historial) < 3:
        return None, 0, "Esperando más datos"
    
    # Análisis ultra-simple pero efectivo
    ultimos_3 = historial[-3:]
    
    # Detectar rachas simples
    if len(set(ultimos_3)) == 1:  # Todos iguales
        resultado = ultimos_3[0]
        if resultado == 'B':
            return 'P', 0.6, "Racha de 3 Dragon - apostar contra"
        elif resultado == 'P':
            return 'B', 0.6, "Racha de 3 Tiger - apostar contra"
        else:
            return 'B', 0.5, "Racha de Tie - volver a Dragon"
    
    # Análisis de frecuencia simple
    b_count = ultimos_3.count('B')
    p_count = ultimos_3.count('P')
    
    if b_count > p_count:
        return 'B', 0.6, f"Dominancia Dragon {b_count}-{p_count}"
    elif p_count > b_count:
        return 'P', 0.6, f"Dominancia Tiger {p_count}-{b_count}"
    else:
        return None, 0, "Empate 50-50, esperar"


async def enviar_senal_telegram(notifier, senal, confianza, razon, historial):
    """Envía la señal a Telegram de forma asíncrona"""
    try:
        emoji = "🔴" if senal == 'B' else "🔵"
        nombre = "DRAGON" if senal == 'B' else "TIGER"
        
        # Formato profesional para Telegram
        mensaje = f"""
🎯 <b>SEÑAL TEMPRANA - BACCARAT</b>

{emoji} <b>APOSTAR A:</b> {nombre} ({senal})
📊 <b>Confianza:</b> {confianza*100:.0f}%
🧠 <b>Análisis:</b> {razon}

📈 <b>Últimos 3:</b> {historial[-3:]}
⏰ <b>Hora:</b> {datetime.now().strftime('%H:%M:%S')}

⚡ <b>¡SEÑAL RÁPIDA!</b>
        """
        
        # Enviar mensaje a Telegram
        success = await notifier.send_message(mensaje, parse_mode="HTML")
        
        if success:
            print(f"✅ Señal enviada: {senal} con confianza {confianza}")
        else:
            print("❌ Error al enviar señal a Telegram")
            
        return success
        
    except Exception as e:
        print(f"❌ Error enviando a Telegram: {e}")
        return False


async def main_async():
    """Bot principal con señales tempranas y Telegram"""
    
    print("🎯 BOT DE SEÑALES TEMPRANAS - BACCARAT")
    print("="*50)
    print("⚡ Señales con solo 3 resultados")
    print("🧠 Análisis simple pero efectivo")
    print("📱 Integración con Telegram activa")
    print("⏰ Nueva señal cada 10 segundos")
    print("="*50)
    
    # Cargar configuración
    config = BotConfig()
    
    # Verificar si Telegram está configurado
    telegram_configured = (
        config.telegram.enabled and
        config.telegram.bot_token and
        config.telegram.chat_id
    )
    if not telegram_configured:
        print("❌ Telegram no está configurado correctamente")
        print("Por favor configura las variables de entorno:")
        print("  - TELEGRAM_BOT_TOKEN")
        print("  - TELEGRAM_CHAT_ID")
        print("  - TELEGRAM_ENABLED=true")
        return
    
    # Inicializar notificador de Telegram
    notifier = TelegramNotifier(
        token=config.telegram.bot_token,
        chat_id=config.telegram.chat_id,
        admin_chat_id=config.telegram.admin_chat_id
    )
    
    # Inicializar conexión con Telegram
    await notifier.initialize()
    
    # Verificar conexión
    if not await notifier.test_connection():
        print("❌ No se pudo conectar con Telegram")
        return
    
    print("✅ Conexión con Telegram establecida")
    
    # Datos iniciales
    historial = ['B', 'P', 'B']  # Datos mínimos para empezar
    print(f"📊 Datos iniciales: {historial}")
    
    iteracion = 0
    
    try:
        while True:
            iteracion += 1
            print(f"\n--- ITERACIÓN {iteracion} ---")
            print(f"📅 {datetime.now().strftime('%H:%M:%S')}")
            
            # Simular nuevo resultado
            resultados = ['B', 'P', 'T']
            probabilidades = [0.446, 0.446, 0.108]  # Probabilidades reales
            nuevo = random.choices(resultados, probabilidades)[0]
            historial.append(nuevo)
            
            # Mantener histórico pequeño
            if len(historial) > 20:
                historial = historial[-20:]
            
            print(f"📊 Total datos: {len(historial)}")
            print(f"Últimos 5: {historial[-5:]}")
            
            # Generar señal temprana
            senal, confianza, razon = generar_senal_temprana(historial)
            
            if senal:
                # Hay señal válida
                emoji = "🔴" if senal == 'B' else "🔵"
                nombre = "DRAGON" if senal == 'B' else "TIGER"
                
                print(f"🎯 SEÑAL DETECTADA: {emoji} {nombre} ({senal})")
                print(f"📊 Confianza: {confianza*100:.0f}%")
                print(f"🧠 Razón: {razon}")
                
                # Enviar a Telegram
                await enviar_senal_telegram(
                    notifier, senal, confianza, razon, historial
                )
                
            else:
                # No hay señal clara
                print(f"⚡ Sin señal clara: {razon}")
                print(f"📊 Últimos 3: {historial[-3:]}")
            
            print("⏰ Esperando 10 segundos...")
            await asyncio.sleep(10)
            
    except KeyboardInterrupt:
        print("\n⏹️ Bot detenido por el usuario")
        print(f"📊 Total de iteraciones: {iteracion}")
    
    finally:
        # Cerrar conexión
        await notifier.close()


def main():
    """Función principal síncrona para ejecutar el bot asíncrono"""
    try:
        asyncio.run(main_async())
    except KeyboardInterrupt:
        print("\n⏹️ Bot detenido por el usuario")


if __name__ == "__main__":
    main()