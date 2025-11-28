"""
Configuración central del Baccarat Bot Avanzado
"""

import os
import json
import logging
from typing import Dict, List
from dataclasses import dataclass
from pathlib import Path

# Importar función setup_logger desde utils
from utils.logger import setup_logger

# Configurar logger global para el módulo
logger = setup_logger(__name__)

@dataclass
class BankrollConfig:
    """Configuración de bankroll"""
    initial_amount: float = 1000.0
    base_unit: float = 10.0
    max_daily_loss: float = 100.0
    max_session_loss: float = 50.0
    daily_profit_target: float = 50.0
    session_profit_target: float = 20.0

@dataclass
class TelegramConfig:
    """Configuración de Telegram"""
    enabled: bool = True
    bot_token: str = ""
    chat_id: str = ""
    admin_chat_id: str = ""
    send_signals: bool = True
    send_reports: bool = True
    report_interval_minutes: int = 30

@dataclass
class NeuralNetworkConfig:
    """Configuración de redes neuronales"""
    sequence_length: int = 20
    features: int = 10
    lstm_units: List[int] = None
    dropout_rate: float = 0.2
    training_epochs: int = 100
    batch_size: int = 32

@dataclass
class MonteCarloConfig:
    """Configuración de Monte Carlo"""
    num_simulations: int = 50000
    num_decks: int = 8
    batch_size: int = 1000
    confidence_level: float = 0.95

@dataclass
class SignalConfig:
    """Configuración de señales"""
    frequency: int = 7  # Cada 7 manos
    min_confidence: str = "MEDIUM"
    max_signals_per_hour: int = 10
    bet_sizing_aggressive: bool = False
    confirm_bets: bool = False
    bet_confirmation_delay: int = 3

@dataclass
class DataSourceConfig:
    """Configuración de fuente de datos"""
    casino_name: str
    api_key: str
    enabled: bool = True
    priority: int = 1
    timeout: int = 30
    max_retries: int = 3

class BotConfig:
    """Configuración principal del bot"""
    
    def __init__(self):
        self.bankroll = BankrollConfig()
        self.telegram = TelegramConfig()
        self.neural_network = NeuralNetworkConfig()
        self.monte_carlo = MonteCarloConfig()
        self.signals = SignalConfig()
        self.data_sources: List[DataSourceConfig] = []
        
        # Configuración general
        self.max_session_duration = 7200  # 2 horas
        self.cooling_period_minutes = 15
        self.emergency_stop_threshold = 0.20  # 20% drawdown
        
        # Cargar desde variables de entorno
        self._load_from_env()
        
        # Validar configuración
        self._validate_config()
    
    def _load_from_env(self):
        """Carga configuración desde variables de entorno"""
        
        # Bankroll
        self.bankroll.initial_amount = float(os.getenv('BANKROLL_INITIAL', '1000.0'))
        self.bankroll.base_unit = float(os.getenv('BANKROLL_BASE_UNIT', '10.0'))
        
        # Telegram
        self.telegram.bot_token = os.getenv('TELEGRAM_BOT_TOKEN', '')
        self.telegram.chat_id = os.getenv('TELEGRAM_CHAT_ID', '')
        self.telegram.admin_chat_id = os.getenv('TELEGRAM_ADMIN_CHAT_ID', '')
        self.telegram.enabled = os.getenv('TELEGRAM_ENABLED', 'true').lower() == 'true'
        
        # Data sources
        casino_names = ['evolution_gaming', 'pragmatic_play', 'playtech', 'betconstruct']
        
        for casino_name in casino_names:
            api_key = os.getenv(f'{casino_name.upper()}_API_KEY', '')
            enabled = os.getenv(f'{casino_name.upper()}_ENABLED', 'false').lower() == 'true'
            
            if api_key and enabled:
                self.data_sources.append(DataSourceConfig(
                    casino_name=casino_name,
                    api_key=api_key,
                    enabled=True
                ))
        
        # Neural network
        self.neural_network.sequence_length = int(os.getenv('NN_SEQUENCE_LENGTH', '20'))
        self.neural_network.training_epochs = int(os.getenv('NN_TRAINING_EPOCHS', '100'))
        
        # Monte Carlo
        self.monte_carlo.num_simulations = int(os.getenv('MC_SIMULATIONS', '50000'))
        
        # Signals
        self.signals.frequency = int(os.getenv('SIGNAL_FREQUENCY', '7'))
        self.signals.min_confidence = os.getenv('SIGNAL_MIN_CONFIDENCE', 'MEDIUM')
    
    def _validate_config(self):
        """Valida la configuración"""
        
        if self.bankroll.initial_amount <= 0:
            raise ValueError("Bankroll inicial debe ser mayor a 0")
        
        if self.bankroll.base_unit <= 0:
            raise ValueError("Unidad base debe ser mayor a 0")
        
        if self.telegram.enabled and (not self.telegram.bot_token or not self.telegram.chat_id):
            logger.warning("Telegram habilitado pero faltan credenciales")
            self.telegram.enabled = False
        
        if not self.data_sources:
            logger.warning("No hay fuentes de datos configuradas. Usando modo demo.")
    
    def to_dict(self) -> dict:
        """Convierte configuración a diccionario"""
        return {
            'bankroll': {
                'initial_amount': self.bankroll.initial_amount,
                'base_unit': self.bankroll.base_unit,
                'max_daily_loss': self.bankroll.max_daily_loss,
                'max_session_loss': self.bankroll.max_session_loss,
                'daily_profit_target': self.bankroll.daily_profit_target,
                'session_profit_target': self.bankroll.session_profit_target
            },
            'telegram': {
                'enabled': self.telegram.enabled,
                'bot_token': '***' if self.telegram.bot_token else '',
                'chat_id': '***' if self.telegram.chat_id else '',
                'send_signals': self.telegram.send_signals,
                'send_reports': self.telegram.send_reports,
                'report_interval_minutes': self.telegram.report_interval_minutes
            },
            'neural_network': {
                'sequence_length': self.neural_network.sequence_length,
                'features': self.neural_network.features,
                'dropout_rate': self.neural_network.dropout_rate,
                'training_epochs': self.neural_network.training_epochs,
                'batch_size': self.neural_network.batch_size
            },
            'monte_carlo': {
                'num_simulations': self.monte_carlo.num_simulations,
                'num_decks': self.monte_carlo.num_decks,
                'batch_size': self.monte_carlo.batch_size,
                'confidence_level': self.monte_carlo.confidence_level
            },
            'signals': {
                'frequency': self.signals.frequency,
                'min_confidence': self.signals.min_confidence,
                'max_signals_per_hour': self.signals.max_signals_per_hour,
                'bet_sizing_aggressive': self.signals.bet_sizing_aggressive,
                'confirm_bets': self.signals.confirm_bets,
                'bet_confirmation_delay': self.signals.bet_confirmation_delay
            },
            'data_sources': [
                {
                    'casino_name': ds.casino_name,
                    'enabled': ds.enabled,
                    'priority': ds.priority,
                    'timeout': ds.timeout,
                    'max_retries': ds.max_retries
                }
                for ds in self.data_sources
            ],
            'general': {
                'max_session_duration': self.max_session_duration,
                'cooling_period_minutes': self.cooling_period_minutes,
                'emergency_stop_threshold': self.emergency_stop_threshold
            }
        }
    
    def save_to_file(self, filepath: str = None):
        """Guarda configuración en archivo"""
        if filepath is None:
            filepath = Path(__file__).parent / 'config.json'
        
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
        
        logger.info(f"Configuración guardada en: {filepath}")
    
    @classmethod
    def load_from_file(cls, filepath: str = None) -> 'BotConfig':
        """Carga configuración desde archivo"""
        if filepath is None:
            filepath = Path(__file__).parent / 'config.json'
        
        config = cls()
        
        if Path(filepath).exists():
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            # Actualizar configuración con datos del archivo
            if 'bankroll' in data:
                for key, value in data['bankroll'].items():
                    if hasattr(config.bankroll, key):
                        setattr(config.bankroll, key, value)
            
            if 'telegram' in data:
                for key, value in data['telegram'].items():
                    if hasattr(config.telegram, key):
                        setattr(config.telegram, key, value)
            
            # Similar para otras secciones...
        
        return config


# Configuración por defecto
DEFAULT_CONFIG = BotConfig()

# Casinos soportados
SUPPORTED_CASINOS = {
    'evolution_gaming': {
        'name': 'Evolution Gaming',
        'description': 'Líder en juegos de casino en vivo',
        'api_url': 'https://api.evolutiongaming.com/live/v2',
        'websocket_url': 'wss://live.evolutiongaming.com/stream',
        'requires_key': True
    },
    'pragmatic_play': {
        'name': 'Pragmatic Play',
        'description': 'Proveedor de casino en vivo premium',
        'api_url': 'https://api.pragmaticplay.com/live/v1',
        'websocket_url': 'wss://live.pragmaticplay.com/ws',
        'requires_key': True
    },
    'playtech': {
        'name': 'Playtech',
        'description': 'Tecnología de casino en vivo avanzada',
        'api_url': 'https://api.playtech.com/live/v3',
        'websocket_url': 'wss://live.playtech.com/stream',
        'requires_key': True
    },
    'betconstruct': {
        'name': 'BetConstruct',
        'description': 'Plataforma de casino en vivo flexible',
        'api_url': 'https://api.betconstruct.com/live/v1',
        'websocket_url': 'wss://live.betconstruct.com/ws',
        'requires_key': True
    },
    'ezugi': {
        'name': 'Ezugi',
        'description': 'Juegos de casino en vivo innovadores',
        'api_url': 'https://api.ezugi.com/live/v1',
        'websocket_url': 'wss://live.ezugi.com/stream',
        'requires_key': True
    },
    'vivo_gaming': {
        'name': 'Vivo Gaming',
        'description': 'Experiencia de casino en vivo latinoamericana',
        'api_url': 'https://api.vivogaming.com/live/v1',
        'websocket_url': 'wss://live.vivogaming.com/ws',
        'requires_key': True
    }
}

# Configuración de estrategias
STRATEGY_CONFIGS = {
    'conservative': {
        'name': 'Conservadora',
        'description': 'Mínimo riesgo, señales de alta confianza solo',
        'min_confidence': 'HIGH',
        'max_bet_size': 3,
        'kelly_fraction': 0.15,
        'stop_loss': 0.03
    },
    'balanced': {
        'name': 'Balanceada',
        'description': 'Balance entre riesgo y recompensa',
        'min_confidence': 'MEDIUM',
        'max_bet_size': 5,
        'kelly_fraction': 0.25,
        'stop_loss': 0.05
    },
    'aggressive': {
        'name': 'Agresiva',
        'description': 'Máxima rentabilidad, mayor riesgo',
        'min_confidence': 'LOW',
        'max_bet_size': 7,
        'kelly_fraction': 0.35,
        'stop_loss': 0.08
    }
}

# Configuración de logging
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
        'detailed': {
            'format': '%(asctime)s [%(levelname)s] %(name)s [%(funcName)s:%(lineno)d] %(message)s'
        }
    },
    'handlers': {
        'default': {
            'level': 'INFO',
            'formatter': 'standard',
            'class': 'logging.StreamHandler'
        },
        'file': {
            'level': 'DEBUG',
            'formatter': 'detailed',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'baccarat_bot.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5
        }
    },
    'loggers': {
        '': {
            'handlers': ['default', 'file'],
            'level': 'INFO',
            'propagate': True
        }
    }
}