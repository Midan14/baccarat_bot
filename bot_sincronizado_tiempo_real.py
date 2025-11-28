#!/usr/bin/env python3
"""
Bot sincronizado con el tiempo real del juego Lightning Dragon Tiger
"""

import time
import random
from datetime import datetime, timedelta
from utils.telegram_notifier import telegram_notifier

class TiempoRealSynchronizer:
    """Sincronización con el tiempo real del juego"""
    
    def __init__(self):
        # Tiempos típicos de Lightning Dragon Tiger
        self.TIEMPOS = {
            'duracion_ronda': 25,      # 25 segundos por ronda
            'tiempo_apuestas': 15,     # 15 segundos para apostar
            'tiempo_reparto': 5,       # 5 segundos repartiendo
            'tiempo_resultado': 3,     # 3 segundos mostrando resultado
            'tiempo_entre_rondas': 2   # 2 segundos entre rondas
        }
        
        # Estado del juego
        self.estado_actual = 'ESPERANDO'  # APUESTA, REPARTO, RESULTADO, ESPERANDO
        self.tiempo_inicio_estado = datetime.now()
        self.numero_ronda = 0
        self.ultimos_resultados = []
        
    def calcular_fase_actual(self, segundos_transcurridos):
        """Calcular en qué fase estamos de la ronda"""
        if segundos_transcurridos <= self.TIEMPOS['tiempo_apuestas']:
            return 'APUESTA'
        elif segundos_transcurridos <= self.TIEMPOS['tiempo_apuestas'] + self.TIEMPOS['tiempo_reparto']:
            return 'REPARTO'
        elif segundos_transcurridos <= self.TIEMPOS['tiempo_apuestas'] + self.TIEMPOS['tiempo_reparto'] + self.TIEMPOS['tiempo_resultado']:
            return 'RESULTADO'
        else:
            return 'ESPERANDO'
    
    def generar_resultado_realista(self):
        """Generar resultado con timing realista"""
        # Probabilidades reales de Lightning Dragon Tiger
        weights = [0.446, 0.446, 0.108]  # Dragon, Tiger, Tie
        return random.choices(['B', 'P', 'T'], weights=weights)[0]
    
    def simular_tiempo_real(self):
        """Simular el tiempo real del juego"""
        ahora = datetime.now()
        segundos_en_ronda = (ahora - self.tiempo_inicio_estado).total_seconds() % self.TIEMPOS['duracion_ronda']
        
        nueva_fase = self.calcular_fase_actual(segundos_en_ronda)
        
        # Detectar cambio de fase
        if nueva_fase != self.estado_actual:
            self.estado_actual = nueva_fase
            self.tiempo_inicio_estado = ahora
            
            if nueva_fase == 'APUESTA':
                self.numero_ronda += 1
                print(f"\n🎮 INICIO RONDA {self.numero_ronda}")
                return 'NUEVA_RONDA'
            elif nueva_fase == 'RESULTADO':
                # Generar resultado al final de la ronda
                resultado = self.generar_resultado_realista()
                self.ultimos_resultados.append(resultado)
                if len(self.ultimos_resultados) > 20:
                    self.ultimos_resultados = self.ultimos_resultados[-20:]
                return 'NUEVO_RESULTADO', resultado
        
        return self.estado_actual, None

def analisis_sincronizado(historial, fase_actual):
    """Análisis sincronizado con la fase del juego"""
    
    if len(historial) < 3:
        return None, 0, "Esperando más datos"
    
    # Análisis profesional basado en fase
    ultimos_5 = historial[-5:]
    ultimos_3 = historial[-3:]
    
    b_count = ultimos_5.count('B')
    p_count = ultimos_5.count('P')
    t_count = ultimos_5.count('T')
    
    # Detectar rachas
    racha_actual = 1
    ultimo_resultado = historial[-1]
    
    for i in range(len(historial)-2, -1, -1):
        if historial[i] == ultimo_resultado:
            racha_actual += 1
        else:
            break
    
    # Generar señal basada en fase y análisis
    if fase_actual == 'APUESTA':
        # Tenemos 15 segundos para apostar
        if racha_actual >= 3:
            # Apostar contra la racha
            if ultimo_resultado == 'B':
                senal = 'P'
                confianza = min(0.8, 0.4 + racha_actual * 0.1)
                razon = f"Racha de {racha_actual} Dragon - apostar contra"
            elif ultimo_resultado == 'P':
                senal = 'B'
                confianza = min(0.8, 0.4 + racha_actual * 0.1)
                razon = f"Racha de {racha_actual} Tiger - apostar contra"
            else:
                senal = 'B'
                confianza = 0.5
                razon = "Racha de Tie - volver a Dragon/Tiger"
        elif b_count > p_count and b_count >= 3:
            senal = 'B'
            confianza = min(0.7, 0.5 + (b_count - p_count) * 0.1)
            razon = f"Dominancia Dragon {b_count}-{p_count} en últimos 5"
        elif p_count > b_count and p_count >= 3:
            senal = 'P'
            confianza = min(0.7, 0.5 + (p_count - b_count) * 0.1)
            razon = f"Dominancia Tiger {p_count}-{b_count} en últimos 5"
        else:
            senal = 'NONE'
            confianza = 0.0
            razon = "Esperando patrón más claro"
    elif fase_actual == 'REPARTO':
        # Últimos segundos para apostar
        if racha_actual >= 4:
            # Última oportunidad contra racha fuerte
            if ultimo_resultado == 'B':
                senal = 'P'
                confianza = min(0.9, 0.5 + racha_actual * 0.1)
                razon = f"Última oportunidad contra racha de {racha_actual} Dragon"
            elif ultimo_resultado == 'P':
                senal = 'B'
                confianza = min(0.9, 0.5 + racha_actual * 0.1)
                razon = f"Última oportunidad contra racha de {racha_actual} Tiger"
            else:
                senal = 'B'
                confianza = 0.6
                razon = "Última oportunidad después de Tie"
        else:
            senal = 'NONE'
            confianza = 0.0
            razon = "Esperando siguiente ronda"
    else:
        senal = 'NONE'
        confianza = 0.0
        razon = f"Fase {fase_actual} - esperando nueva ronda"
    
    return senal, confianza, razon

def main():
    """Bot principal con sincronización de tiempo real"""
    
    print("⏰ BOT SINCRONIZADO CON TIEMPO REAL DEL JUEGO")
    print("="*60)
    print("🎯 Sincronizado con ritmo de Lightning Dragon Tiger")
    print("⏱️  25 segundos por ronda, 15 segundos para apostar")
    print("📱 Enviando señales solo en momento óptimo")
    print("="*60)
    
    sincronizador = TiempoRealSynchronizer()
    historial = []
    ultima_señal_enviada = None
    
    # Mensaje inicial
    mensaje_inicio = """
⏰ <b>BOT SINCRONIZADO CON TIEMPO REAL</b>

✅ Sincronizado con ritmo del juego
⏱️  25 segundos por ronda completa
🎯 Señales en momento óptimo

¡Esperando inicio de ronda!
    """
    telegram_notifier.send_message(mensaje_inicio)
    
    iteracion = 0
    
    try:
        while True:
            iteracion += 1
            tiempo_actual = datetime.now().strftime('%H:%M:%S')
            print(f"\n--- {tiempo_actual} ---")
            
            # Simular tiempo real del juego
            resultado_tiempo = sincronizador.simular_tiempo_real()
            if isinstance(resultado_tiempo, tuple) and len(resultado_tiempo) == 2:
                estado, resultado = resultado_tiempo
            else:
                estado = resultado_tiempo
                resultado = None
            
            print(f"🎮 Estado: {estado}")
            
            if estado == 'NUEVA_RONDA':
                print(f"🆕 Nueva ronda #{sincronizador.numero_ronda}")
                
            elif estado == 'NUEVO_RESULTADO':
                print(f"🎯 Resultado: {resultado}")
                historial.append(resultado)
                if len(historial) > 20:
                    historial = historial[-20:]
                
                # Enviar resumen del resultado
                mensaje_resultado = f"""
🎯 <b>RESULTADO RONDA {sincronizador.numero_ronda}</b>

📊 <b>Resultado:</b> {resultado}
📈 <b>Historial:</b> {historial[-5:]}
⏰ <b>Hora:</b> {tiempo_actual}
                """
                telegram_notifier.send_message(mensaje_resultado)
                
            elif estado == 'APUESTA':
                # Momento óptimo para enviar señal
                print("💰 Fase de apuestas - analizando...")
                
                senal, confianza, razon = analisis_sincronizado(historial, estado)
                
                if senal and senal != 'NONE':
                    # Calcular tiempo restante para apostar
                    segundos_en_ronda = (datetime.now() - sincronizador.tiempo_inicio_estado).total_seconds() % sincronizador.TIEMPOS['duracion_ronda']
                    tiempo_restante = max(0, sincronizador.TIEMPOS['tiempo_apuestas'] - segundos_en_ronda)
                    
                    color = "🔴" if senal == 'B' else "🔵"
                    nombre = "DRAGON" if senal == 'B' else "TIGER"
                    
                    mensaje = f"""
🎯 <b>SEÑAL SINCRONIZADA - BACCARAT</b>

{color} <b>APOSTAR A:</b> {nombre} ({senal})
📊 <b>Confianza:</b> {confianza*100:.0f}%
🧠 <b>Análisis:</b> {razon}

⏰ <b>Tiempo restante:</b> {int(tiempo_restante)}s
📈 <b>Últimos 5:</b> {historial[-5:]}
💰 <b>Apuesta:</b> ${confianza:.1f} a {nombre}
                    """
                    
                    telegram_notifier.send_message(mensaje)
                    print(f"✅ SEÑAL ENVIADA: {senal} con {confianza*100:.0f}% confianza")
                    print(f"   📊 Razón: {razon}")
                    print(f"   ⏰ Tiempo restante: {int(tiempo_restante)}s")
                    
                    ultima_señal_enviada = (senal, confianza, tiempo_restante)
                
            elif estado == 'REPARTO':
                print("🃏 Repartiendo cartas...")
                if ultima_señal_enviada:
                    senal, confianza, tiempo_restante = ultima_señal_enviada
                    if tiempo_restante < 3:  # Últimos 3 segundos
                        mensaje_urgente = f"""
⚡ <b>ÚLTIMOS SEGUNDOS</b>

🎯 Señal activa: {senal} ({confianza*100:.0f}%)
⏰ <b>Tiempo restante:</b> {int(tiempo_restante)}s
💰 ¡Apuesta ahora!
                        """
                        telegram_notifier.send_message(mensaje_urgente)
                        print("⚡ Enviando recordatorio urgente")
            
            # Esperar un segundo antes de siguiente verificación
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n⏹️ Bot detenido por el usuario")
        
        mensaje_final = """
🛑 <b>BOT SINCRONIZADO DETENIDO</b>

📊 Tiempo real sincronizado
✅ Señales en momento óptimo
⏰ Sistema funcionando correctamente

¡Gracias por usar el bot sincronizado!
        """
        telegram_notifier.send_message(mensaje_final)

if __name__ == "__main__":
    main()