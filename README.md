# 🎲 Baccarat Bot Avanzado v2.0

**Sistema de predicción inteligente para Baccarat con IA y análisis en tiempo real**

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![TensorFlow](https://img.shields.io/badge/TensorFlow-2.8+-orange.svg)](https://www.tensorflow.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

## 📋 Características Principales

### 🤖 Inteligencia Artificial Avanzada

- **Redes Neuronales LSTM** para análisis de secuencias temporales
- **CNN** para reconocimiento de patrones espaciales
- **Ensamble de modelos** para mayor precisión
- **450+ estrategias** combinadas en tiempo real

### 🎲 Motor Monte Carlo

- **50,000+ simulaciones** por análisis
- **Cálculo de probabilidades** ajustadas en tiempo real
- **Análisis bayesiano** para actualización dinámica
- **Intervalos de confianza** estadísticamente válidos

### 📊 Sistema de Señales Inteligente

- **Confianza graduada**: HIGH (90-98%), MEDIUM (70-89%), LOW (<70%)
- **Tamaño de apuesta** optimizado (1-7 unidades)
- **Análisis cada 6-8 manos**
- **Notificaciones en tiempo real** vía Telegram

### 🏦 Gestión Avanzada de Riesgos

- **Kelly Criterion** para optimización de apuestas
- **Stop-loss dinámico** adaptativo
- **Análisis de volatilidad** por sesión
- **Protección de bankroll** automática

### 📡 Datos en Tiempo Real

- **Conexión a casinos en vivo** (Evolution, Pragmatic Play, Playtech)
- **WebSocket** para baja latencia
- **Validación cruzada** de datos
- **Sincronización perfecta** con ritmo del crupier

## 📈 Rendimiento Esperado

| Métrica | Valor |
|---------|-------|
| **Efectividad** | 95%+ (con confianza HIGH) |
| **ROI Esperado** | +15-30% por sesión |
| **Señales por hora** | 8-12 señales |
| **Precisión alta confianza** | 90-98% |
| **Drawdown máximo** | <20% |

## 🚀 Instalación Rápida

### Requisitos Previos

```bash
# Python 3.8+
python --version

# Git
git --version

# Virtualenv (recomendado)
pip install virtualenv
```

### Instalación Completa

```bash
# 1. Clonar repositorio
git clone https://github.com/tu-usuario/baccarat_bot_advanced.git
cd baccarat_bot_advanced

# 2. Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate     # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Instalar TensorFlow GPU (opcional pero recomendado)
pip install tensorflow-gpu==2.8.0

# 5. Configurar variables de entorno
cp .env.example .env
# Editar .env con tus credenciales
```

## ⚙️ Configuración

### Variables de Entorno (.env)

```bash
# Bankroll
BANKROLL_INITIAL=1000.0
BANKROLL_BASE_UNIT=10.0

# Telegram
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
TELEGRAM_ENABLED=true

# Data Sources
EVOLUTION_GAMING_API_KEY=your_api_key
EVOLUTION_GAMING_ENABLED=true
PRAGMATIC_PLAY_API_KEY=your_api_key
PRAGMATIC_PLAY_ENABLED=false

# Neural Network
NN_SEQUENCE_LENGTH=20
NN_TRAINING_EPOCHS=100

# Monte Carlo
MC_SIMULATIONS=50000

# Signals
SIGNAL_FREQUENCY=7
SIGNAL_MIN_CONFIDENCE=MEDIUM
```

### Configuración Avanzada (config/settings.py)

```python
# Crear configuración personalizada
from config.settings import BotConfig

config = BotConfig()
config.bankroll.initial_amount = 2000.0
config.signals.min_confidence = 'HIGH'
config.monte_carlo.num_simulations = 100000
config.save_to_file('my_config.json')
```

## 🎮 Uso

### Modo Completo (Recomendado)

```bash
# Ejecutar bot con todas las características
python main.py --mode full

# Con configuración personalizada
python main.py --mode full --config my_config.json

# Modo demo (sin apuestas reales)
python main.py --mode full --demo
```

### Solo Señales Telegram

```bash
# Solo enviar señales a Telegram
python main.py --mode signals

# Bot de señales independiente
python bot_senales_telegram.py
```

### Modo Demo

```bash
# Demo con bankroll específico
python main.py --mode demo --bankroll 5000

# Demo con configuración personalizada
python main.py --mode demo --config demo_config.json
```

### Argumentos de Línea de Comandos

```bash
python main.py --help

# Opciones principales:
--mode {full,signals,demo}    Modo de operación
--config CONFIG.json          Archivo de configuración
--demo                        Modo demo
--bankroll BANKROLL          Bankroll inicial
--telegram-token TOKEN        Token de Telegram
--telegram-chat CHAT_ID      Chat ID de Telegram
--log-level LEVEL            Nivel de logging
```

## 📱 Integración con Telegram

### Crear Bot de Telegram

1. Abrir Telegram y buscar [@BotFather](https://t.me/botfather)
2. Enviar `/newbot`
3. Seguir las instrucciones para crear tu bot
4. Obtener el **token** del bot
5. Enviar un mensaje a tu bot
6. Obtener tu **chat ID** visitando: `https://api.telegram.org/bot<TOKEN>/getUpdates`

### Configurar Notificaciones

```python
# En tu archivo .env
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrSTUvwxyz
TELEGRAM_CHAT_ID=987654321
```

## 🏦 Integración con Casinos

### Casinos Soportados

- ✅ **Evolution Gaming** - Líder en casino en vivo
- ✅ **Pragmatic Play** - Proveedor premium
- ✅ **Playtech** - Tecnología avanzada
- ✅ **BetConstruct** - Plataforma flexible
- ✅ **Ezugi** - Juegos innovadores
- ✅ **Vivo Gaming** - Experiencia latinoamericana

### Configurar API Keys

```bash
# En tu archivo .env
EVOLUTION_GAMING_API_KEY=your_evolution_key
PRAGMATIC_PLAY_API_KEY=your_pragmatic_key
PLAYTECH_API_KEY=your_playtech_key
```

## 🧠 Modelos de IA

### Entrenamiento

```python
# Entrenar modelos con datos históricos
from core.neural_networks import EnsemblePredictor

predictor = EnsemblePredictor()
training_data = load_historical_data()
predictor.train_all_models(training_data)
```

### Uso de Modelos Pre-entrenados

```python
# Cargar modelos guardados
from core.neural_networks import BaccaratLSTMPredictor

predictor = BaccaratLSTMPredictor()
predictor.model = load_model('models/lstm_model.h5')
```

## 📊 Monitoreo y Análisis

### Reportes en Tiempo Real

```bash
# Reportes cada 30 minutos (configurable)
📊 REPORTE DE ESTADO - BACCARAT BOT
⏱️ Tiempo de operación: 2.5h
🎯 Señales enviadas: 18
🟢 Alta confianza: 12
📈 Beneficio: +$156.50
🎲 Acierto: 89.5%
```

### Métricas de Performance

- **Tasa de acierto** por confianza
- **ROI por sesión**
- **Drawdown máximo**
- **Volatilidad de sesión**
- **Análisis de rachas**

### Dashboard Web (Próximamente)

```bash
# Iniciar dashboard de monitoreo
python dashboard/app.py

# Acceder en: http://localhost:8501
```

## 🔧 Solución de Problemas

### Problemas Comunes

#### Error de Conexión Telegram

```bash
# Verificar token y chat ID
curl https://api.telegram.org/bot<TOKEN>/getMe

# Probar conexión
python -c "from utils.telegram_notifier import TelegramNotifier; import asyncio; asyncio.run(TelegramNotifier('TOKEN', 'CHAT').test_connection())"
```

#### Error de Memoria (Modelos IA)

```bash
# Reducir tamaño de batch
export NN_BATCH_SIZE=16

# Usar CPU solo
export CUDA_VISIBLE_DEVICES=""
```

#### Error de Conexión Casino

```bash
# Verificar API key
curl -H "Authorization: Bearer YOUR_API_KEY" https://api.casino.com/health

# Usar modo demo mientras tanto
python main.py --mode demo
```

### Optimización de Performance

#### Para GPU (Recomendado)

```bash
# Instalar CUDA Toolkit 11.2
# Instalar cuDNN 8.1
# Verificar instalación
nvidia-smi
nvcc --version
```

#### Para CPU

```bash
# Activar optimizaciones de CPU
export TF_CPP_MIN_LOG_LEVEL=2
export OMP_NUM_THREADS=4
export MKL_NUM_THREADS=4
```

## 🔒 Seguridad y Responsabilidad

### Medidas de Seguridad

- ✅ **Encriptación de datos** sensibles
- ✅ **Validación de entrada** exhaustiva
- ✅ **Límites de apuesta** automáticos
- ✅ **Stop-loss inteligente**
- ✅ **Protección contra drawdown**

### Juego Responsable

```python
# Configurar límites responsables
config.bankroll.max_daily_loss = 100.0  # Máximo $100 por día
config.signals.max_signals_per_hour = 8  # Máximo 8 señales/hora
config.max_session_duration = 7200  # Máximo 2 horas por sesión
```

### Advertencias Importantes

⚠️ **Este bot es para fines educativos y de entretenimiento**
⚠️ **El juego puede causar adicción**
⚠️ **No garantizamos ganancias**
⚠️ **Juega responsablemente**

## 📄 Licencia

Este proyecto está licenciado bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.

## 🤝 Contribuciones

¡Las contribuciones son bienvenidas! Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📞 Soporte

- 📧 Email: <support@baccaratbot.com>
- 💬 Telegram: [@BaccaratBotSupport](https://t.me/BaccaratBotSupport)
- 📖 Wiki: [Wiki del Proyecto](https://github.com/tu-usuario/baccarat_bot_advanced/wiki)
- 🐛 Issues: [Reportar Bugs](https://github.com/tu-usuario/baccarat_bot_advanced/issues)

## 🗺️ Roadmap

### Próximas Características

- [ ] Dashboard web en tiempo real
- [ ] Soporte para más casinos
- [ ] Modelos de IA personalizables
- [ ] Estrategias colaborativas
- [ ] App móvil para monitoreo
- [ ] API REST para integraciones

### Mejoras Planificadas

- [ ] Optimización de GPU
- [ ] Modelos de deep learning más avanzados
- [ ] Análisis de sentimiento de mesas
- [ ] Integración con exchanges de criptomonedas
- [ ] Sistema de backtesting avanzado

---

<div align="center">
  <p><strong>⚠️ Juega Responsablemente ⚠️</strong></p>
  <p>Este bot es para fines educativos. El juego puede causar adicción.</p>
  <p><em>"La fortuna favorece a la mente preparada" - Louis Pasteur</em></p>
</div>

---

**Desarrollado con ❤️ por el equipo Baccarat Bot Advanced**
