#!/usr/bin/env python3
"""
Script de configuración para Lightning Dragon Tiger de Evolution Gaming
Automatiza la configuración del bot para este juego específico
"""

import os
import sys
import shutil
from pathlib import Path

def configure_for_lightning_dragontiger():
    """Configurar el bot para Lightning Dragon Tiger"""
    
    print("🐉 Configurando Baccarat Bot para Lightning Dragon Tiger... 🐅")
    
    # Verificar que estamos en el directorio correcto
    if not os.path.exists('main.py'):
        print("❌ Error: Debes ejecutar este script desde el directorio del proyecto baccarat_bot")
        sys.exit(1)
    
    # 1. Actualizar configuración principal
    print("\n📋 Actualizando configuración principal...")
    update_main_config()
    
    # 2. Actualizar locators
    print("\n🎯 Actualizando locators para Lightning Dragon Tiger...")
    update_locators()
    
    # 3. Actualizar motor de predicción
    print("\n🧠 Actualizando motor de predicción...")
    update_prediction_engine()
    
    # 4. Crear backup de configuración anterior
    print("\n💾 Creando backup de configuración anterior...")
    create_config_backup()
    
    print("\n✅ Configuración completada exitosamente!")
    print("\n📖 El bot ahora está configurado para:")
    print("   - Juego: Lightning Dragon Tiger (Evolution Gaming)")
    print("   - URL: https://20bet.com/es/live-casino/game/evolution/lightningdragontiger")
    print("   - Apuestas: Dragon, Tiger, Tie")
    print("   - Multiplicadores Lightning: Activados")
    
    print("\n🚀 Para ejecutar el bot:")
    print("   source venv/bin/activate")
    print("   python main.py")

def update_main_config():
    """Actualizar el archivo de configuración principal"""
    config_content = '''# config/settings.py
import os
from dataclasses import dataclass
from typing import Dict, List
from config.lightning_dragontiger_config import lightning_dragontiger_config

@dataclass
class BrowserConfig:
    """Configuración del navegador"""
    headless: bool = False
    user_agent: str = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/120.0.0.0 Safari/537.36")
    viewport_width: int = 1920
    viewport_height: int = 1080
    timeout: int = 30000
    stealth_mode: bool = True


@dataclass
class PredictionConfig:
    """Configuración de los algoritmos de predicción"""
    trend_sequence_length: int = 3
    frequency_window: int = 20
    min_data_points: int = 10
    lightning_analysis: bool = True


@dataclass
class BankrollConfig:
    """Configuración de gestión de bankroll"""
    base_bet: float = 1.0
    max_bet: float = 100.0
    strategy: str = "martingale"
    stop_loss: float = 1000.0
    stop_win: float = 500.0


@dataclass
class ExecutionConfig:
    """Configuración de ejecución"""
    min_delay: float = 0.8
    max_delay: float = 2.5
    max_retries: int = 3
    retry_delay: float = 5.0
    betting_timeout: int = 12  # Tiempo límite para apostar en Lightning Dragon Tiger


class Settings:
    """Configuración principal de la aplicación"""
    
    def __init__(self):
        self.browser = BrowserConfig()
        self.prediction = PredictionConfig()
        self.bankroll = BankrollConfig()
        self.execution = ExecutionConfig()
        
        # Configuración específica de Lightning Dragon Tiger
        self.game_config = lightning_dragontiger_config
        self.url = self.game_config.game_url
        
        # Rutas
        self.log_dir = "logs"
        self.screenshots_dir = "screenshots"
        
        self._create_directories()
    
    def _create_directories(self):
        """Crear directorios necesarios"""
        os.makedirs(self.log_dir, exist_ok=True)
        os.makedirs(self.screenshots_dir, exist_ok=True)


# Instancia global de configuración
settings = Settings()
'''
    
    with open('config/settings.py', 'w') as f:
        f.write(config_content)
    
    print("✅ Configuración principal actualizada")

def update_locators():
    """Actualizar los locators para Lightning Dragon Tiger"""
    # Copiar el archivo de locators específicos
    src_locators = 'config/lightning_dragontiger_locators.py'
    dst_locators = 'config/locators.py'
    
    if os.path.exists(src_locators):
        shutil.copy2(src_locators, dst_locators)
        print("✅ Locators actualizados para Lightning Dragon Tiger")
    else:
        print("⚠️  No se encontró el archivo de locators específicos")

def update_prediction_engine():
    """Actualizar el motor de predicción para Lightning Dragon Tiger"""
    # Copiar el motor específico
    src_engine = 'core/lightning_dragontiger_engine.py'
    dst_engine = 'core/prediction_engine.py'
    
    if os.path.exists(src_engine):
        shutil.copy2(src_engine, dst_engine)
        print("✅ Motor de predicción actualizado para Lightning Dragon Tiger")
    else:
        print("⚠️  No se encontró el motor de predicción específico")

def create_config_backup():
    """Crear backup de la configuración anterior"""
    backup_dir = "config/backups"
    os.makedirs(backup_dir, exist_ok=True)
    
    # Archivos a respaldar
    files_to_backup = [
        'config/settings.py',
        'config/locators.py',
        'core/prediction_engine.py'
    ]
    
    for file_path in files_to_backup:
        if os.path.exists(file_path):
            # Crear nombre con timestamp
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.basename(file_path)
            backup_path = f"{backup_dir}/{filename}_{timestamp}.backup"
            
            shutil.copy2(file_path, backup_path)
            print(f"✅ Backup creado: {backup_path}")

if __name__ == "__main__":
    configure_for_lightning_dragontiger()