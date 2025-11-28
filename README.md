# Baccarat Bot 🤖

Un bot automatizado inteligente para jugar Baccarat en línea utilizando análisis predictivo y gestión de riesgos avanzada.

## Características ✨

- **Automatización Completa**: Navegación y control automatizado del juego
- **Análisis Predictivo**: Múltiples modelos de predicción para mejorar las tasas de ganancia
- **Gestión de Riesgos**: Sistema inteligente de gestión de bankroll y límites de sesión
- **Registro Detallado**: Sistema completo de logging con rotación de archivos
- **Interfaz Configurable**: Opciones flexibles de configuración
- **Modo Headless**: Ejecución en segundo plano sin interfaz gráfica

## Arquitectura 🏗️

```
baccarat_bot/
├── config/                 # Configuración y localizadores
│   ├── settings.py        # Configuración general
│   └── locators.py        # Localizadores de elementos web
├── core/                  # Lógica principal
│   ├── browser.py         # Gestión del navegador
│   ├── data_acquisition.py # Adquisición de datos del juego
│   ├── prediction_engine.py # Motor de predicción
│   ├── decision_engine.py  # Motor de decisiones
│   └── execution_engine.py # Motor de ejecución
├── utils/                 # Utilidades
│   ├── logger.py          # Sistema de logging
│   └── helpers.py         # Funciones auxiliares
├── tests/                 # Pruebas unitarias
└── main.py               # Punto de entrada principal
```

## Instalación 🚀

1. **Clonar el repositorio**:

```bash
git clone https://github.com/tu-usuario/baccarat_bot.git
cd baccarat_bot
```

2. **Crear entorno virtual**:

```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. **Instalar dependencias**:

```bash
pip install -r requirements.txt
```

4. **Instalar ChromeDriver** (automático con webdriver-manager):

```bash
# El webdriver-manager se encargará de descargar ChromeDriver automáticamente
```

## Uso 🎯

### Ejecución Básica

```bash
python main.py --url "https://ejemplo.com/baccarat" --balance 1000
```

### Opciones Avanzadas

```bash
python main.py \
    --url "https://ejemplo.com/baccarat" \
    --balance 1000 \
    --min-bet 5 \
    --max-bet 100 \
    --no-headless \
    --log-level DEBUG
```

### Parámetros

| Parámetro | Descripción | Valor por Defecto |
|-----------|-------------|-------------------|
| `--url` | URL del juego de Baccarat | Requerido |
| `--balance` | Balance inicial | Requerido |
| `--min-bet` | Apuesta mínima | 1.0 |
| `--max-bet` | Apuesta máxima | 100.0 |
| `--headless` | Modo sin cabeza | True |
| `--no-headless` | Mostrar navegador | False |
| `--log-level` | Nivel de logging | INFO |

## Configuración ⚙️

### Configuración del Juego

Edita `config/settings.py` para ajustar:

- **Límites de apuesta**: `min_bet`, `max_bet`
- **Configuración del navegador**: `headless`, `timeout`
- **Parámetros de predicción**: `history_size`, `confidence_threshold`
- **Límites de sesión**: `max_sessions`, `session_timeout`

### Localizadores Web

Los localizadores de elementos web están en `config/locators.py`. Ajusta según el sitio web específico.

## Estrategia de Predicción 🧠

El bot utiliza múltiples modelos de predicción:

1. **Basado en Patrones**: Detecta patrones repetitivos en la historia
2. **Estadístico**: Análisis de frecuencias y probabilidades
3. **Basado en Tendencias**: Identifica tendencias y rachas

### Gestión de Riesgos

- **Control de Bankroll**: Apuestas basadas en el balance actual
- **Límites de Sesión**: Máximo de pérdidas, ganancias y número de apuestas
- **Análisis de Riesgo**: Evaluación continua del riesgo actual
- **Sistema de Stops**: Detención automática en condiciones adversas

## Logging 📝

El sistema de logging incluye:

- **Consola**: Mensajes de INFO y superiores
- **Archivo Principal**: Todos los mensajes DEBUG y superiores
- **Archivo de Errores**: Solo mensajes ERROR
- **Rotación Automática**: Archivos de hasta 10MB con 5 copias de respaldo

## Pruebas 🧪

Ejecutar las pruebas unitarias:

```bash
# Todas las pruebas
python -m pytest tests/

# Con cobertura
python -m pytest tests/ --cov=core --cov-report=html

# Pruebas específicas
python -m pytest tests/test_predictions.py
```

## Seguridad 🔒

- **Sin credenciales almacenadas**: No se almacenan contraseñas
- **Navegador aislado**: Ejecución en navegador separado
- **Logging seguro**: Información sensible no se registra
- **Validación de entrada**: Todas las entradas son validadas

## Solución de Problemas 🔧

### Error: "ChromeDriver no encontrado"

```bash
# Asegúrate de que webdriver-manager esté instalado
pip install webdriver-manager
```

### Error: "Elemento no encontrado"

- Verifica los localizadores en `config/locators.py`
- Ajusta los tiempos de espera en `config/settings.py`

### Error: "Apuesta no procesada"

- Verifica que los límites de apuesta sean correctos
- Comprueba que el balance sea suficiente

## Contribuir 🤝

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## Licencia 📄

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

## Descargo de Responsabilidad ⚠️

**IMPORTANTE**: Este bot es para fines educativos y de investigación únicamente. El juego puede ser adictivo y conlleva riesgos financieros.

- **No garantizamos ganancias**: El bot no garantiza ganancias
- **Juega responsablemente**: Nunca apuestes más de lo que puedas perder
- **Verifica legalidad**: Asegúrate de que el juego online sea legal en tu jurisdicción
- **Riesgo de pérdida**: Puedes perder dinero real usando este bot

## Contacto 📧

Para preguntas o soporte, por favor abre un issue en GitHub.

---

**⚠️ Advertencia**: El juego puede causar adicción. Si tienes problemas con el juego, busca ayuda profesional.
