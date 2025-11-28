# config/settings.py
import os
from dataclasses import dataclass
from dotenv import load_dotenv
from config.lightning_dragontiger_config import lightning_dragontiger_config

# Cargar variables de entorno desde .env
load_dotenv()


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
    betting_timeout: int = 12  # Tiempo límite para apostar


@dataclass
class TelegramConfig:
    """Configuración de Telegram para notificaciones"""
    default_token = "7892748327:AAHF874evLoi1JQNrOJrRe9ZQ8-Grq6f-g8"
    bot_token: str = os.getenv("TELEGRAM_BOT_TOKEN", default_token)
    chat_id: str = os.getenv("TELEGRAM_CHAT_ID", "631443236")
    enabled: bool = os.getenv("TELEGRAM_ENABLED", "true").lower() == "true"


class Settings:
    """Configuración principal de la aplicación"""
    
    def __init__(self):
        self.browser = BrowserConfig()
        self.prediction = PredictionConfig()
        self.bankroll = BankrollConfig()
        self.execution = ExecutionConfig()
        self.telegram = TelegramConfig()
        
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
