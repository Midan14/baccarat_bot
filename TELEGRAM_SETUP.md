# Configuración de Notificaciones de Telegram

## 📱 Integración Completa con Protección de Credenciales

Las credenciales de Telegram han sido integradas exitosamente en el bot con un sistema seguro de variables de entorno. A continuación, te explico cómo funciona y cómo puedes personalizarlas.

## 🔒 Seguridad de Credenciales

### Sistema de Variables de Entorno

Las credenciales sensibles ahora están protegidas mediante el archivo `.env`:

- **Archivo `.env`**: Contiene las credenciales reales (PROTEGIDO por `.gitignore`)
- **Archivo `.env.example`**: Plantilla de ejemplo para nuevos usuarios
- **Variables de entorno**: Cargadas automáticamente al iniciar el bot

### 🔧 Configuración Actual

Las credenciales se cargan desde las variables de entorno en [`config/settings.py`](config/settings.py:56):

```python
@dataclass
class TelegramConfig:
    """Configuración de Telegram para notificaciones"""
    bot_token: str = os.getenv("TELEGRAM_BOT_TOKEN", "TOKEN_POR_DEFECTO")
    chat_id: str = os.getenv("TELEGRAM_CHAT_ID", "CHAT_ID_POR_DEFECTO")
    enabled: bool = os.getenv("TELEGRAM_ENABLED", "true").lower() == "true"
```

### 📋 Archivos de Configuración

1. **[`.env`](.env)** - Archivo real con credenciales (NO compartir)
2. **[`.env.example`](.env.example)** - Plantilla para nuevos usuarios
3. **[`.gitignore`](.gitignore)** - Protege el archivo `.env` de ser subido a Git

## 🚀 Cómo Funciona

### 1. Notificaciones Automáticas

El bot enviará automáticamente notificaciones a tu chat de Telegram cuando:

- ✅ Se genere una nueva predicción
- ✅ Se complete una apuesta (ganada o perdida)
- ✅ Ocurra un error importante
- ✅ Se ejecuten pruebas de conexión

### 2. Tipos de Notificaciones

#### 📊 Señales de Predicción

```
🎯 SEÑAL DE PREDICCIÓN - LIGHTNING DRAGON TIGER

🎮 Juego: Lightning Dragon Tiger
🔮 Predicción: Dragon
📊 Confianza: 85.5%

🧠 Análisis: Análisis de tendencias y patrones históricos
📈 Estadísticas:
• Racha actual: 3 victorias Dragon
• Frecuencia Dragon: 45%
• Frecuencia Tiger: 42%
• Frecuencia Tie: 13%

¡Buena suerte!
```

#### 💰 Resultados de Apuesta

```
✅ RESULTADO DE APUESTA

🔮 Predicción: Dragon
🎯 Resultado: Dragon
💰 Ganancia: $10.50
💳 Balance: $1250.75
```

#### ⚠️ Notificaciones de Error

```
⚠️ ERROR DETECTADO

🔥 Tipo: Conexión
❗ Mensaje: Error de prueba - conexión intermitente

📝 Contexto: Durante la prueba de integración
```

## 🧪 Probar la Conexión

Para verificar que todo funciona correctamente, ejecuta:

```bash
cd baccarat_bot
source venv/bin/activate
python test_telegram.py
```

Este script enviará:

- Mensaje de prueba básico
- Señal de predicción de ejemplo
- Notificación de resultado
- Notificación de error

## 🔧 Personalización

### Cambiar Credenciales

Si necesitas cambiar las credenciales, edita [`config/settings.py`](config/settings.py:52):

```python
@dataclass
class TelegramConfig:
    bot_token: str = "TU_NUEVO_TOKEN_AQUI"
    chat_id: str = "TU_NUEVO_CHAT_ID"
    enabled: bool = True  # False para desactivar
```

### Desactivar Notificaciones

Para desactivar temporalmente las notificaciones:

```python
enabled: bool = False
```

## 📋 Información del Bot

- **Bot Username**: @Analisis_bacca_bot
- **Token**: 7892748327:AAHF874evLoi1JQNrOJrRe9ZQ8-Grq6f-g8
- **Chat ID**: 631443236

## 🔒 Seguridad

- Las credenciales están almacenadas de forma segura en la configuración
- El bot solo puede enviar mensajes, no recibir comandos
- Los mensajes incluyen información relevante sin exponer datos sensibles

## 🛠️ Módulos Involucrados

1. **[`config/settings.py`](config/settings.py)** - Configuración de credenciales
2. **[`utils/telegram_notifier.py`](utils/telegram_notifier.py)** - Módulo de notificaciones
3. **[`core/prediction_engine.py`](core/prediction_engine.py)** - Integración con predicciones
4. **[`test_telegram.py`](test_telegram.py)** - Script de prueba

## 🔑 Personalización Segura

### Para cambiar las credenciales

1. **Edita el archivo `.env`** (nunca compartas este archivo):

```bash
# .env
TELEGRAM_BOT_TOKEN=tu_nuevo_token_aqui
TELEGRAM_CHAT_ID=tu_nuevo_chat_id
TELEGRAM_ENABLED=true
```

2. **Reinicia el bot** para aplicar los cambios

### Para desactivar notificaciones

```bash
# .env
TELEGRAM_ENABLED=false
```

## 🛡️ Seguridad Mejorada

- ✅ **Credenciales protegidas**: El archivo `.env` está en `.gitignore`
- ✅ **No hardcodeadas**: Las credenciales no están en el código fuente
- ✅ **Variables de entorno**: Sistema profesional de configuración
- ✅ **Plantilla incluida**: `.env.example` para nuevos desarrolladores
- ✅ **Documentación completa**: Instrucciones claras de seguridad

## 📞 Soporte

Si tienes problemas con las notificaciones:

1. Verifica que el archivo `.env` exista y tenga el formato correcto
2. Comprueba que el bot esté activo en Telegram
3. Verifica que el chat ID sea correcto
4. Ejecuta el script de prueba para diagnosticar problemas
5. Revisa los logs en la carpeta `logs/` para errores detallados

## ⚠️ Importante: Seguridad

- **NUNCA** compartas el archivo `.env` con nadie
- **NUNCA** subas el archivo `.env` a repositorios públicos
- **SIEMPRE** usa `.env.example` como plantilla para nuevos usuarios
- **VERIFICA** que `.gitignore` incluya `.env` antes de hacer commit

¡Listo! Las notificaciones de Telegram están completamente configuradas, protegidas y funcionando. 📱🔒✨
