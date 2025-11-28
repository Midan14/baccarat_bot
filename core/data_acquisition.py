# core/data_acquisition.py
from typing import List, Dict, Any, Optional
from playwright.sync_api import Page
from config.locators import locators
from config.settings import settings
from utils.logger import logger
from utils.helpers import helpers

class DataAcquisition:
    """Sistema robusto de adquisición de datos"""
    
    def __init__(self, page: Page):
        self.page = page
        self.current_history_hash = None
    
    def wait_for_game_load(self, timeout: int = 10000) -> bool:
        """Esperar a que el juego cargue completamente"""
        try:
            logger.info("Esperando a que el juego cargue...")
            self.page.wait_for_selector(locators.history_container, timeout=timeout)
            self.page.wait_for_selector(locators.bet_panel, timeout=timeout)
            logger.info("Juego cargado exitosamente")
            return True
        except Exception as e:
            logger.error(f"Error al cargar el juego: {str(e)}")
            return False
    
    def extract_game_history(self) -> Optional[List[str]]:
        """Extraer y validar el historial del juego"""
        try:
            history_container = self.page.query_selector(locators.history_container)
            if not history_container:
                logger.warning("No se encontró el contenedor del historial")
                return None
            
            result_elements = history_container.query_selector_all(locators.result_elements)
            history = []
            
            for element in result_elements:
                result = self._parse_result_element(element)
                if result:
                    history.append(result)
            
            # Validar y verificar cambios
            if self._validate_and_update_history(history):
                logger.info(f"Historial extraído: {len(history)} resultados")
                return history
            else:
                return None
                
        except Exception as e:
            logger.error(f"Error al extraer historial: {str(e)}")
            return None
    
    def _parse_result_element(self, element) -> Optional[str]:
        """Parsear elemento individual del resultado"""
        try:
            # Método 1: Por clase CSS
            class_name = element.get_attribute('class') or ''
            
            if 'banker' in class_name.lower() or 'rojo' in class_name.lower():
                return 'B'
            elif 'player' in class_name.lower() or 'azul' in class_name.lower():
                return 'P'
            elif 'tie' in class_name.lower() or 'empate' in class_name.lower() or 'verde' in class_name.lower():
                return 'E'
            
            # Método 2: Por texto
            text_content = element.text_content() or ''
            if 'B' in text_content.upper():
                return 'B'
            elif 'P' in text_content.upper():
                return 'P'
            elif 'E' in text_content.upper():
                return 'E'
            
            return None
            
        except Exception as e:
            logger.debug(f"Error parseando elemento: {str(e)}")
            return None
    
    def _validate_and_update_history(self, history: List[str]) -> bool:
        """Validar historial y detectar cambios"""
        if not helpers.validate_history(history):
            logger.warning("Historial no válido")
            return False
        
        current_hash = helpers.calculate_hash(str(history))
        
        if current_hash != self.current_history_hash:
            self.current_history_hash = current_hash
            return True
        
        return False  # Sin cambios
    
    def get_game_state(self) -> Dict[str, Any]:
        """Obtener estado completo del juego"""
        try:
            state = {
                'history': self.extract_game_history(),
                'timestamp': helpers.get_timestamp(),
                'current_hand': self._get_current_hand(),
                'time_remaining': self._get_time_remaining(),
                'betting_open': self._is_betting_open()
            }
            return state
        except Exception as e:
            logger.error(f"Error obteniendo estado del juego: {str(e)}")
            return {}
    
    def _get_current_hand(self) -> Optional[str]:
        """Obtener número de mano actual"""
        try:
            element = self.page.query_selector(locators.current_hand)
            return element.text_content() if element else None
        except:
            return None
    
    def _get_time_remaining(self) -> Optional[str]:
        """Obtener tiempo restante"""
        try:
            element = self.page.query_selector(locators.timer)
            return element.text_content() if element else None
        except:
            return None
    
    def _is_betting_open(self) -> bool:
        """Verificar si la apuesta está abierta"""
        try:
            status_element = self.page.query_selector(locators.game_status)
            if status_element:
                status_text = status_element.text_content().lower()
                return 'apuesta' in status_text or 'betting' in status_text
            return True  # Asumir abierto si no se puede determinar
        except:
            return True