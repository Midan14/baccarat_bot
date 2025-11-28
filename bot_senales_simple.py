#!/usr/bin/env python3
"""
Bot ultra-simple que solo genera señales
"""

import random
import time
from datetime import datetime

# Datos de demostración simples
historial = ['B', 'P', 'B', 'B', 'P', 'P', 'B', 'P', 'B', 'P', 'B', 'B', 'P', 'B', 'P']

def generar_senal_simple(historial):
    """Genera señal simple basada en el último resultado"""
    if len(historial) < 3:
        return "ESPERANDO_DATOS", 0.0
    
    ultimos_3 = historial[-3:]
    b_count = ultimos_3.count('B')
    p_count = ultimos_3.count('P')
    
    print(f"Últimos 3 resultados: {ultimos_3}")
    print(f"Conteo - B: {b_count}, P: {p_count}")
    
    if b_count >= 2:
        return "B", 0.6
    elif p_count >= 2:
        return "P", 0.6
    else:
        return "NONE", 0.0

def main():
    print("🎯 BOT DE SEÑALES ULTRA-SIMPLE")
    print("="*50)
    print("Generando señales cada 2 segundos...")
    print("="*50)
    
    iteracion = 0
    
    while True:
        iteracion += 1
        print(f"\n--- ITERACIÓN {iteracion} ---")
        print(f"📅 {datetime.now().strftime('%H:%M:%S')}")
        
        # Agregar nuevo resultado aleatorio
        nuevo = random.choice(['B', 'P', 'B', 'P', 'B'])  # 80% B para más señales
        historial.append(nuevo)
        
        print(f"📊 Historial actual: {len(historial)} resultados")
        print(f"Últimos 5: {historial[-5:]}")
        
        # Generar señal
        senal, confianza = generar_senal_simple(historial)
        
        print(f"🔮 SEÑAL DETECTADA:")
        print(f"   🎯 SEÑAL: {senal}")
        print(f"   📈 CONFIANZA: {confianza}")
        
        if senal != "ESPERANDO_DATOS" and senal != "NONE":
            print(f"   💰 RECOMENDACIÓN: Apostar a {senal}")
            print(f"   📊 MONTO SUGERIDO: ${confianza:.1f}")
        
        # Pequeña pausa
        time.sleep(2)
        
        # Limite para demo
        if iteracion > 20:
            break
    
    print("\n" + "="*50)
    print("✅ DEMO COMPLETADA")
    print("✅ Se generaron señales en cada iteración")
    print("="*50)

if __name__ == "__main__":
    main()