#!/usr/bin/env python3
"""
Script de prueba para verificar la conexión de Telegram
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.telegram_notifier import telegram_notifier


def test_telegram_connection():
    """Probar la conexión con Telegram"""
    print("🧪 Probando conexión con Telegram...")
    
    # Test 1: Conexión básica
    print("1. Probando conexión básica...")
    if telegram_notifier.test_connection():
        print("   ✅ Conexión exitosa")
    else:
        print("   ❌ Error de conexión")
        return False
    
    # Test 2: Enviar mensaje de prueba
    print("2. Enviando mensaje de prueba...")
    if telegram_notifier.send_message("🧪 <b>Mensaje de prueba</b>\n\n"
                                      "Este es un mensaje de prueba desde el "
                                      "bot de Baccarat.\n\n"
                                      "Si ves este mensaje, la integración "
                                      "está funcionando correctamente. ✅"):
        print("   ✅ Mensaje enviado exitosamente")
    else:
        print("   ❌ Error al enviar mensaje")
        return False
    
    # Test 3: Enviar señal de predicción de prueba
    print("3. Enviando señal de predicción de prueba...")
    if telegram_notifier.send_prediction_signal(
        game_type="Lightning Dragon Tiger",
        prediction="Dragon",
        confidence=85.5,
        reasoning="Análisis de tendencias y patrones históricos",
        additional_info={
            "Racha actual": "3 victorias Dragon",
            "Frecuencia Dragon": "45%",
            "Frecuencia Tiger": "42%",
            "Frecuencia Tie": "13%"
        }
    ):
        print("   ✅ Señal de predicción enviada")
    else:
        print("   ❌ Error al enviar señal")
        return False
    
    # Test 4: Enviar notificación de resultado
    print("4. Enviando notificación de resultado...")
    if telegram_notifier.send_result_notification(
        prediction="Dragon",
        result="Dragon",
        won=True,
        profit=10.50,
        balance=1250.75
    ):
        print("   ✅ Notificación de resultado enviada")
    else:
        print("   ❌ Error al enviar notificación")
        return False
    
    # Test 5: Enviar notificación de error
    print("5. Enviando notificación de error...")
    if telegram_notifier.send_error_notification(
        error_type="Conexión",
        error_message="Error de prueba - conexión intermitente",
        context="Durante la prueba de integración"
    ):
        print("   ✅ Notificación de error enviada")
    else:
        print("   ❌ Error al enviar notificación de error")
        return False
    
    print("\n🎉 ¡Todas las pruebas pasaron exitosamente!")
    print("📱 Las notificaciones de Telegram están configuradas correctamente.")
    print(f"🔑 Bot Token: {telegram_notifier.token[:10]}...")
    print(f"💬 Chat ID: {telegram_notifier.chat_id}")
    
    return True

if __name__ == "__main__":
    try:
        success = test_telegram_connection()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n❌ Prueba interrumpida por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error durante la prueba: {e}")
        sys.exit(1)