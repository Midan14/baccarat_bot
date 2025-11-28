# utils/logger.py
import logging
import sys
from datetime import datetime
from pathlib import Path
from config.settings import settings

class BotLogger:
    """Sistema de logging robusto para el bot"""
    
    def __init__(self, name: str = "BaccaratBot"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        # Evitar logs duplicados
        if not self.logger.handlers:
            self._setup_handlers()
    
    def _setup_handlers(self):
        """Configurar handlers de logging"""
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Handler para archivo
        log_file = Path(settings.log_dir) / f"baccarat_bot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        
        # Handler para consola
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def info(self, message: str):
        self.logger.info(message)
    
    def warning(self, message: str):
        self.logger.warning(message)
    
    def error(self, message: str, exc_info=False):
        self.logger.error(message, exc_info=exc_info)
    
    def debug(self, message: str):
        self.logger.debug(message)
    
    def bet_placed(self, bet_type: str, amount: float, signal: str):
        """Log especializado para apuestas"""
        self.info(f"🎯 APUESTA REALIZADA - Tipo: {bet_type} | Cantidad: {amount} | Señal: {signal}")

# Logger global
logger = BotLogger()