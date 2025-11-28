"""
Sistema de logging avanzado para el Baccarat Bot
"""

import logging
import logging.handlers
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

class ColoredFormatter(logging.Formatter):
    """Formato de logging con colores para terminal"""
    
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m'        # Reset
    }
    
    def format(self, record):
        # Agregar color al nivel
        color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        reset = self.COLORS['RESET']
        
        # Formato con color
        record.levelname = f"{color}{record.levelname}{reset}"
        
        return super().format(record)

class BaccaratLogger:
    """Logger personalizado para el bot de baccarat"""
    
    def __init__(self, name: str, log_level: str = 'INFO', log_dir: str = 'logs'):
        self.name = name
        self.log_level = getattr(logging, log_level.upper())
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Crear logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(self.log_level)
        
        # Limpiar handlers existentes
        self.logger.handlers.clear()
        
        # Configurar handlers
        self._setup_console_handler()
        self._setup_file_handlers()
        
    def _setup_console_handler(self):
        """Configura handler para consola"""
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(self.log_level)
        
        # Formato con colores para terminal
        console_format = ColoredFormatter(
            '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
            datefmt='%H:%M:%S'
        )
        console_handler.setFormatter(console_format)
        
        self.logger.addHandler(console_handler)
    
    def _setup_file_handlers(self):
        """Configura handlers para archivos"""
        
        # Handler para archivo principal
        main_handler = logging.handlers.RotatingFileHandler(
            self.log_dir / 'baccarat_bot.log',
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        main_handler.setLevel(self.log_level)
        
        # Formato detallado para archivo
        file_format = logging.Formatter(
            '%(asctime)s [%(levelname)s] %(name)s [%(funcName)s:%(lineno)d] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        main_handler.setFormatter(file_format)
        
        self.logger.addHandler(main_handler)
        
        # Handler separado para señales
        signals_handler = logging.handlers.RotatingFileHandler(
            self.log_dir / 'signals.log',
            maxBytes=5*1024*1024,  # 5MB
            backupCount=3,
            encoding='utf-8'
        )
        signals_handler.setLevel(logging.INFO)
        
        # Formato simple para señales
        signals_format = logging.Formatter(
            '%(asctime)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        signals_handler.setFormatter(signals_format)
        
        self.logger.addHandler(signals_handler)
        
        # Handler para errores críticos
        error_handler = logging.handlers.RotatingFileHandler(
            self.log_dir / 'errors.log',
            maxBytes=5*1024*1024,  # 5MB
            backupCount=3,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(file_format)
        
        self.logger.addHandler(error_handler)
    
    def get_logger(self) -> logging.Logger:
        """Obtiene el logger configurado"""
        return self.logger
    
    def log_signal(self, signal_data: dict):
        """Log especial para señales"""
        signal_logger = logging.getLogger('signals')
        signal_logger.info(f"SEÑAL: {json.dumps(signal_data, default=str)}")
    
    def log_bet(self, bet_data: dict):
        """Log especial para apuestas"""
        bet_logger = logging.getLogger('bets')
        bet_logger.info(f"APUESTA: {json.dumps(bet_data, default=str)}")
    
    def log_error_detail(self, error: Exception, context: str = None):
        """Log detallado de errores"""
        import traceback
        
        error_msg = f"ERROR en {context}: {str(error)}\n"
        error_msg += f"Traceback:\n{traceback.format_exc()}"
        
        self.logger.error(error_msg)

def setup_logger(name: str = 'baccarat_bot', log_level: str = None) -> logging.Logger:
    """
    Configura y retorna un logger
    
    Args:
        name: Nombre del logger
        log_level: Nivel de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        
    Returns:
        Logger configurado
    """
    if log_level is None:
        log_level = os.getenv('LOG_LEVEL', 'INFO')
    
    # Crear logger personalizado
    baccarat_logger = BaccaratLogger(name, log_level)
    
    return baccarat_logger.get_logger()

# Loggers pre-configurados
def get_bot_logger() -> logging.Logger:
    """Obtiene logger para el bot principal"""
    return setup_logger('baccarat_bot')

def get_neural_logger() -> logging.Logger:
    """Obtiene logger para redes neuronales"""
    return setup_logger('neural_networks')

def get_signal_logger() -> logging.Logger:
    """Obtiene logger para señales"""
    return setup_logger('signal_generator')

def get_risk_logger() -> logging.Logger:
    """Obtiene logger para gestión de riesgos"""
    return setup_logger('risk_management')

def get_data_logger() -> logging.Logger:
    """Obtiene logger para adquisición de datos"""
    return setup_logger('data_acquisition')

# Configuración de logging para módulos externos
def setup_external_loggers():
    """Configura logging para módulos externos"""
    
    # Reducir logging de librerías externas
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('aiohttp').setLevel(logging.WARNING)
    logging.getLogger('asyncio').setLevel(logging.WARNING)
    logging.getLogger('websocket').setLevel(logging.WARNING)
    
    # TensorFlow logging
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # ERROR only
    logging.getLogger('tensorflow').setLevel(logging.ERROR)

# Inicializar configuración de logging externo
setup_external_loggers()

# Funciones utilitarias de logging
class LogContext:
    """Context manager para logging con información adicional"""
    
    def __init__(self, logger: logging.Logger, context: str):
        self.logger = logger
        self.context = context
        self.start_time = None
    
    def __enter__(self):
        self.start_time = datetime.now()
        self.logger.info(f"Iniciando {self.context}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = datetime.now() - self.start_time
        if exc_type is None:
            self.logger.info(f"Completado {self.context} en {duration.total_seconds():.2f}s")
        else:
            self.logger.error(f"Error en {self.context}: {exc_val}")

def log_function_call(logger: logging.Logger):
    """Decorador para loggear llamadas a funciones"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            logger.debug(f"Llamando {func.__name__} con args={args}, kwargs={kwargs}")
            try:
                result = func(*args, **kwargs)
                logger.debug(f"{func.__name__} completado exitosamente")
                return result
            except Exception as e:
                logger.error(f"Error en {func.__name__}: {e}")
                raise
        return wrapper
    return decorator

# Métricas de performance
class PerformanceMetrics:
    """Métricas de performance para logging"""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.metrics = {}
    
    def start_timer(self, name: str):
        """Inicia un temporizador"""
        self.metrics[f"{name}_start"] = datetime.now()
    
    def end_timer(self, name: str):
        """Finaliza un temporizador y loggea el resultado"""
        start_key = f"{name}_start"
        if start_key in self.metrics:
            duration = datetime.now() - self.metrics[start_key]
            self.logger.info(f"{name} tomó {duration.total_seconds():.3f}s")
            del self.metrics[start_key]
    
    def log_metric(self, name: str, value):
        """Loggea una métrica"""
        self.logger.info(f"Métrica {name}: {value}")
        self.metrics[name] = value