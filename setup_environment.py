#!/usr/bin/env python3
"""
Script de configuración del entorno para baccarat_bot
Automatiza la instalación de dependencias y navegadores
"""

import subprocess
import sys
import os

def run_command(command, description):
    """Ejecuta un comando y maneja errores"""
    print(f"\n🔧 {description}...")
    try:
        subprocess.run(
            command, shell=True, check=True,
            capture_output=True, text=True
        )
        print(f"✅ {description} completado")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error en {description}: {e}")
        print(f"Salida de error: {e.stderr}")
        return False


def main():
    """Función principal de configuración"""
    print("🚀 Iniciando configuración del entorno para baccarat_bot...")
    
    # Verificar que estamos en el directorio correcto
    if not os.path.exists('requirements.txt'):
        print("❌ Error: No se encontró requirements.txt. "
              "Asegúrate de estar en el directorio del proyecto.")
        sys.exit(1)
    
    # Activar entorno virtual
    if not run_command("source venv/bin/activate",
                       "Activando entorno virtual"):
        print("❌ Error: No se pudo activar el entorno virtual")
        sys.exit(1)
    
    # Instalar dependencias principales
    dependencies = [
        "selenium webdriver-manager requests python-dotenv "
        "pyyaml colorama tqdm",
        "numpy pandas scikit-learn matplotlib",
        "pytest pytest-cov pytest-playwright pytest-asyncio "
        "flake8 black mypy playwright"
    ]
    
    for dep_group in dependencies:
        if not run_command(
            f"pip install {dep_group}",
            f"Instalando dependencias: {dep_group}"
        ):
            print("⚠️  Algunas dependencias podrían haber fallado, "
                  "continuando...")
    
    # Instalar navegadores de Playwright
    print("\n🌐 Instalando navegadores para Playwright...")
    if not run_command("playwright install chromium", "Instalando Chromium"):
        print("⚠️  Playwright Chromium podría haber fallado")
    
    # Verificar instalación
    print("\n📋 Verificando instalación...")
    run_command("pip list", "Listando paquetes instalados")
    
    print("\n🎉 ¡Configuración del entorno completada!")
    print("\n📖 Instrucciones de uso:")
    print("1. Activa el entorno virtual: source venv/bin/activate")
    print("2. O usa el script: ./activate_env.sh")
    print("3. Ejecuta el bot: python main.py")
    print("4. Para desactivar: deactivate")

if __name__ == "__main__":
    main()