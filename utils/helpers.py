# utils/helpers.py
import random
import time
import hashlib
from typing import List, Optional, Dict, Any
from datetime import datetime
from config.settings import settings

class Helpers:
    """Funciones auxiliares para el bot"""
    
    @staticmethod
    def random_delay(min_delay: Optional[float] = None, max_delay: Optional[float] = None):
        """Pausa aleatoria entre acciones"""
        min_val = min_delay or settings.execution.min_delay
        max_val = max_delay or settings.execution.max_delay
        delay = random.uniform(min_val, max_val)
        time.sleep(delay)
    
    @staticmethod
    def calculate_hash(data: str) -> str:
        """Calcular hash de datos para verificación"""
        return hashlib.md5(data.encode()).hexdigest()
    
    @staticmethod
    def validate_history(history: List[str]) -> bool:
        """Validar que el historial sea consistente"""
        if not history:
            return False
        
        valid_values = ['B', 'P', 'E']
        return all(item in valid_values for item in history)
    
    @staticmethod
    def format_signal(signal_data: Dict[str, Any]) -> str:
        """Formatear datos de señal para logging"""
        return (f"Señal: {signal_data.get('signal', 'NONE')} | "
                f"Confianza: {signal_data.get('confidence', 0):.2f} | "
                f"Algoritmo: {signal_data.get('algorithm', 'Unknown')}")
    
    @staticmethod
    def get_timestamp() -> str:
        """Obtener timestamp formateado"""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

helpers = Helpers()