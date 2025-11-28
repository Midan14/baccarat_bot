# Configuración del Entorno Virtual - Baccarat Bot

## 📋 Requisitos Previos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)
- Sistema operativo macOS, Linux o Windows

## 🚀 Instalación Rápida

### 1. Crear y activar el entorno virtual

```bash
# Crear entorno virtual
python3 -m venv venv

# Activar entorno virtual
# En macOS/Linux:
source venv/bin/activate

# En Windows:
venv\Scripts\activate
```

### 2. Instalar dependencias

```bash
# Instalar todas las dependencias
pip install -r requirements.txt

# Instalar navegadores para Playwright
playwright install chromium
```

### 3. Verificar instalación

```bash
# Verificar que todo esté instalado
pip list

# Ejecutar pruebas
python -m pytest tests/ -v
```

## 📁 Estructura del Entorno

```
baccarat_bot/
├── venv/                    # Entorno virtual
├── activate_env.sh         # Script de activación rápida
├── setup_environment.py    # Script de configuración automática
├── requirements.txt        # Dependencias del proyecto
├── main.py                 # Archivo principal
├── config/                 # Configuraciones
├── core/                   # Núcleo del bot
├── utils/                  # Utilidades
└── tests/                  # Pruebas
```

## 🔧 Scripts de Ayuda

### Script de Activación Rápida

```bash
# Hacer ejecutable el script
chmod +x activate_env.sh

# Activar entorno virtual
./activate_env.sh
```

### Script de Configuración Automática

```bash
# Ejecutar configuración completa
python setup_environment.py
```

## 📦 Dependencias Principales

### Web Automation

- **selenium** (4.15.2) - Automatización de navegador
- **webdriver-manager** (4.0.1) - Gestión de drivers
- **playwright** (1.40.0) - Automatización moderna de navegador

### Data Science & ML

- **numpy** (1.26.2) - Computación numérica
- **pandas** (2.1.4) - Manipulación de datos
- **scikit-learn** (1.3.2) - Machine learning
- **matplotlib** (3.8.2) - Visualización

### Testing & Development

- **pytest** (7.4.3) - Framework de pruebas
- **pytest-cov** (4.1.0) - Cobertura de código
- **pytest-playwright** (0.4.3) - Pruebas con Playwright
- **flake8** (6.1.0) - Análisis de código
- **black** (23.9.1) - Formateador de código
- **mypy** (1.6.1) - Comprobación de tipos

### Utilidades

- **requests** (2.31.0) - HTTP requests
- **python-dotenv** (1.0.0) - Variables de entorno
- **pyyaml** (6.0.1) - YAML parser
- **colorama** (0.4.6) - Colores en terminal
- **tqdm** (4.66.1) - Barras de progreso

## 🧪 Ejecutar Pruebas

```bash
# Activar entorno virtual
source venv/bin/activate

# Ejecutar todas las pruebas
python -m pytest tests/ -v

# Ejecutar pruebas con cobertura
python -m pytest tests/ --cov=core --cov=utils

# Ejecutar pruebas de Playwright
python -m pytest tests/ --browser chromium
```

## 🎯 Uso del Bot

```bash
# Activar entorno virtual
source venv/bin/activate

# Ejecutar el bot principal
python main.py

# Ejecutar con configuración específica
python main.py --config config/settings.py
```

## 🐛 Solución de Problemas

### Error: "Cannot import 'setuptools.build_meta'"

```bash
# Actualizar pip, setuptools y wheel
pip install --upgrade pip setuptools wheel
```

### Error: "module 'pkgutil' has no attribute 'ImpImporter'"

```bash
# Instalar versión compatible de setuptools
pip install setuptools==65.5.0
```

### Error de compatibilidad con numpy

```bash
# Instalar numpy compatible con tu versión de Python
pip install numpy --upgrade
```

### Playwright no encuentra navegadores

```bash
# Instalar navegadores manualmente
playwright install
playwright install chromium
playwright install firefox
playwright install webkit
```

## 🔍 Verificación del Entorno

Para verificar que todo está funcionando correctamente:

```python
# test_environment.py
import sys
print(f"Python: {sys.version}")

try:
    import selenium
    print(f"✅ Selenium: {selenium.__version__}")
except ImportError:
    print("❌ Selenium no instalado")

try:
    import numpy
    print(f"✅ NumPy: {numpy.__version__}")
except ImportError:
    print("❌ NumPy no instalado")

try:
    import pandas
    print(f"✅ Pandas: {pandas.__version__}")
except ImportError:
    print("❌ Pandas no instalado")

try:
    import pytest
    print(f"✅ Pytest: {pytest.__version__}")
except ImportError:
    print("❌ Pytest no instalado")
```

## 📚 Comandos Útiles

```bash
# Desactivar entorno virtual
deactivate

# Verificar versión de Python
python --version

# Verificar pip
pip --version

# Actualizar pip
pip install --upgrade pip

# Limpiar caché de pip
pip cache purge

# Exportar dependencias actuales
pip freeze > requirements_current.txt

# Instalar desde requirements.txt
pip install -r requirements.txt

# Desinstalar paquete
pip uninstall nombre_paquete
```

## 📝 Notas Importantes

1. **Siempre activa el entorno virtual** antes de trabajar en el proyecto
2. **No subas el directorio `venv/`** a control de versiones
3. **Actualiza requirements.txt** cuando agregues nuevas dependencias
4. **Ejecuta pruebas** antes de hacer commit de cambios importantes
5. **Usa el script de activación** para facilitar el trabajo diario

## 🆘 Soporte

Si encuentras problemas con la configuración del entorno:

1. Verifica que tengas Python 3.8+ instalado
2. Asegúrate de activar el entorno virtual correctamente
3. Revisa los mensajes de error en la terminal
4. Intenta ejecutar el script de configuración automática
5. Consulta la documentación oficial de cada paquete

¡El entorno virtual está listo para usar! 🎉
