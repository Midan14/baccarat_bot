#!/bin/bash

# Script de instalación para Baccarat Bot Avanzado
# Compatible con Linux y macOS

set -e  # Salir en caso de error

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Funciones de utilidad
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verificar sistema operativo
OS="$(uname -s)"
case "${OS}" in
    Linux*)     PLATFORM=Linux;;
    Darwin*)    PLATFORM=Mac;;
    *)          log_error "Sistema operativo no soportado: ${OS}"; exit 1;;
esac

log_info "Detectado sistema operativo: ${PLATFORM}"

# Verificar Python
if command -v python3 &>/dev/null; then
    PYTHON_CMD="python3"
elif command -v python &>/dev/null; then
    PYTHON_CMD="python"
else
    log_error "Python no está instalado. Por favor instala Python 3.8+ primero."
    exit 1
fi

PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | awk '{print $2}')
log_info "Python detectado: $PYTHON_VERSION"

# Verificar versión de Python
MIN_PYTHON_VERSION="3.8"
if ! $PYTHON_CMD -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
    log_error "Se requiere Python 3.8 o superior. Versión actual: $PYTHON_VERSION"
    exit 1
fi

# Verificar pip
if ! command -v pip &>/dev/null && ! command -v pip3 &>/dev/null; then
    log_error "pip no está instalado. Por favor instala pip primero."
    exit 1
fi

PIP_CMD="pip"
if command -v pip3 &>/dev/null; then
    PIP_CMD="pip3"
fi

log_info "pip detectado: $PIP_CMD"

# Función para instalar dependencias del sistema
install_system_deps() {
    log_info "Instalando dependencias del sistema..."
    
    case "${PLATFORM}" in
        Linux)
            if command -v apt-get &>/dev/null; then
                # Ubuntu/Debian
                sudo apt-get update
                sudo apt-get install -y build-essential python3-dev python3-pip
                sudo apt-get install -y libhdf5-dev libatlas-base-dev liblapack-dev
                sudo apt-get install -y wget curl git
            elif command -v yum &>/dev/null; then
                # CentOS/RHEL
                sudo yum groupinstall -y "Development Tools"
                sudo yum install -y python3-devel python3-pip
                sudo yum install -y wget curl git
            elif command -v dnf &>/dev/null; then
                # Fedora
                sudo dnf groupinstall -y "Development Tools"
                sudo dnf install -y python3-devel python3-pip
                sudo dnf install -y wget curl git
            else
                log_warning "No se pudo detectar el gestor de paquetes. Instala manualmente: build-essential, python3-dev, libhdf5-dev"
            fi
            ;;
        Mac)
            if command -v brew &>/dev/null; then
                # macOS con Homebrew
                brew install wget curl git
                brew install hdf5
            else
                log_warning "Homebrew no encontrado. Instala Xcode Command Line Tools: xcode-select --install"
            fi
            ;;
    esac
}

# Función para crear entorno virtual
create_virtualenv() {
    log_info "Creando entorno virtual..."
    
    if [ -d "venv" ]; then
        log_warning "El entorno virtual ya existe. Eliminando..."
        rm -rf venv
    fi
    
    $PYTHON_CMD -m venv venv
    
    if [ $? -eq 0 ]; then
        log_success "Entorno virtual creado exitosamente"
    else
        log_error "Error creando entorno virtual"
        exit 1
    fi
}

# Función para activar entorno virtual
activate_virtualenv() {
    log_info "Activando entorno virtual..."
    
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
        log_success "Entorno virtual activado"
    elif [ -f "venv/Scripts/activate" ]; then
        source venv/Scripts/activate
        log_success "Entorno virtual activado"
    else
        log_error "No se pudo encontrar el script de activación del entorno virtual"
        exit 1
    fi
}

# Función para actualizar pip
update_pip() {
    log_info "Actualizando pip..."
    $PIP_CMD install --upgrade pip setuptools wheel
    
    if [ $? -eq 0 ]; then
        log_success "pip actualizado exitosamente"
    else
        log_warning "Error actualizando pip, continuando de todos modos..."
    fi
}

# Función para instalar dependencias de Python
install_python_deps() {
    log_info "Instalando dependencias de Python..."
    
    # Instalar primero las dependencias básicas
    $PIP_CMD install numpy pandas scipy
    
    # Instalar TensorFlow (CPU primero para evitar problemas)
    log_info "Instalando TensorFlow..."
    $PIP_CMD install tensorflow==2.8.0
    
    # Instalar el resto de dependencias
    $PIP_CMD install -r requirements.txt
    
    if [ $? -eq 0 ]; then
        log_success "Dependencias de Python instaladas exitosamente"
    else
        log_error "Error instalando dependencias de Python"
        exit 1
    fi
}

# Función para verificar instalación de TensorFlow
check_tensorflow() {
    log_info "Verificando instalación de TensorFlow..."
    
    if $PYTHON_CMD -c "import tensorflow as tf; print('TensorFlow version:', tf.__version__)" 2>/dev/null; then
        log_success "TensorFlow está instalado correctamente"
        
        # Verificar GPU
        if $PYTHON_CMD -c "import tensorflow as tf; print('GPU disponible:', tf.config.list_physical_devices('GPU'))" 2>/dev/null | grep -q "GPU"; then
            log_success "GPU detectada y disponible para TensorFlow"
        else
            log_warning "GPU no detectada. Usando CPU (más lento)"
        fi
    else
        log_error "TensorFlow no está instalado correctamente"
        exit 1
    fi
}

# Función para crear archivo de configuración
create_config() {
    log_info "Creando archivo de configuración..."
    
    if [ ! -f ".env" ]; then
        cp .env.example .env
        log_success "Archivo .env creado desde .env.example"
        log_warning "¡IMPORTANTE! Edita el archivo .env con tus credenciales antes de ejecutar el bot"
    else
        log_warning "El archivo .env ya existe. Saltando creación."
    fi
}

# Función para crear directorios necesarios
create_directories() {
    log_info "Creando directorios necesarios..."
    
    mkdir -p logs
    mkdir -p data
    mkdir -p models
    mkdir -p backups
    mkdir -p config
    
    log_success "Directorios creados exitosamente"
}

# Función para configurar permisos
setup_permissions() {
    log_info "Configurando permisos..."
    
    chmod +x main.py
    chmod +x bot_avanzado_completo.py
    chmod +x bot_senales_telegram.py
    
    log_success "Permisos configurados"
}

# Función para realizar prueba de instalación
test_installation() {
    log_info "Realizando prueba de instalación..."
    
    # Probar importación de módulos principales
    if $PYTHON_CMD -c "
import sys
sys.path.insert(0, '.')
try:
    import numpy
    import pandas
    import tensorflow
    print('✓ Módulos principales importados correctamente')
except ImportError as e:
    print(f'✗ Error importando: {e}')
    sys.exit(1)
"; then
        log_success "Prueba de instalación exitosa"
    else
        log_error "Error en prueba de instalación"
        exit 1
    fi
}

# Función para mostrar instrucciones post-instalación
show_post_install_instructions() {
    echo ""
    echo "🎉 ¡Instalación completada exitosamente!"
    echo ""
    echo "📋 Próximos pasos:"
    echo ""
    echo "1. Configurar credenciales:"
    echo "   • Edita el archivo .env con tus credenciales"
    echo "   • Obtén tu token de Telegram de @BotFather"
    echo "   • Obtén API keys de los casinos que uses"
    echo ""
    echo "2. Activar entorno virtual:"
    echo "   source venv/bin/activate  # Linux/Mac"
    echo "   venv\\Scripts\\activate    # Windows"
    echo ""
    echo "3. Ejecutar el bot:"
    echo "   python main.py --mode demo              # Modo demo"
    echo "   python main.py --mode full              # Modo completo"
    echo "   python main.py --mode signals           # Solo señales"
    echo ""
    echo "4. Verificar funcionamiento:"
    echo "   python -c 'from main import main; import asyncio; asyncio.run(main())'"
    echo ""
    echo "📚 Documentación adicional:"
    echo "   • README.md - Documentación completa"
    echo "   • config/settings.py - Configuración avanzada"
    echo "   • requirements.txt - Dependencias"
    echo ""
    echo "🔧 Comandos útiles:"
    echo "   python main.py --help                    # Ayuda"
    echo "   python main.py --mode demo --bankroll 5000  # Demo con bankroll"
    echo "   python main.py --config custom.json      # Config personalizada"
    echo ""
    echo "⚠️  IMPORTANTE:"
    echo "   • Nunca compartas tu archivo .env"
    echo "   • Usa modo demo primero para probar"
    echo "   • Configura límites de riesgo responsables"
    echo "   • El juego puede causar adicción"
    echo ""
    echo "🎲 ¡Listo para comenzar! 🎲"
}

# Función principal de instalación
main() {
    echo "🎲 Baccarat Bot Avanzado - Instalador"
    echo "======================================"
    echo ""
    
    # Verificar que estamos en el directorio correcto
    if [ ! -f "requirements.txt" ] || [ ! -f "main.py" ]; then
        log_error "No se encontraron los archivos necesarios. Asegúrate de estar en el directorio del proyecto."
        exit 1
    fi
    
    # Preguntar al usuario
    echo "Este script instalará el Baccarat Bot Avanzado con todas sus dependencias."
    echo ""
    read -p "¿Deseas continuar? (s/n) " -n 1 -r
    echo ""
    
    if [[ ! $REPLY =~ ^[Ss]$ ]]; then
        log_info "Instalación cancelada por el usuario"
        exit 0
    fi
    
    # Instalación paso a paso
    {
        install_system_deps
        create_virtualenv
        activate_virtualenv
        update_pip
        install_python_deps
        check_tensorflow
        create_config
        create_directories
        setup_permissions
        test_installation
        show_post_install_instructions
    } || {
        log_error "Error durante la instalación"
        exit 1
    }
}

# Ejecutar instalación
main "$@"