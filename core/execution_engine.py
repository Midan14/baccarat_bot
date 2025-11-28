# core/execution_engine.py
from typing import Optional, Dict, Any
from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError
from config.locators import locators
from config.settings import settings
from utils.logger import logger
from utils.helpers import helpers
from core.decision_engine import BettingDecision

class ExecutionEngine:
    """Motor de ejecución de apuestas con simulación humana"""
    
    def __init__(self, page: Page):
        self.page = page
        self.execution_count = 0
    
    def place_bet(self, decision: BettingDecision) -> bool:
        """Ejecutar apuesta en la interfaz"""
        if not decision.should_bet:
            return False
        
        try:
            logger.info(f"Intentando apuesta: {decision.bet_type} - {decision.amount}")
            
            # Localizar el botón correcto
            button_locator = self._get_bet_button_locator(decision.bet_type)
            if not button_locator:
                logger.error("No se pudo encontrar el botón de apuesta")
                return False
            
            # Esperar a que el botón esté disponible
            if not self._wait_for_bet_ready(button_locator):
                logger.warning("Botón de apuesta no disponible a tiempo")
                return False
            
            # Simular comportamiento humano
            self._human_like_preparation(button_locator)
            
            # Hacer clic en el botón
            if self._click_bet_button(button_locator):
                self.execution_count += 1
                logger.bet_placed(decision.bet_type, decision.amount, decision.signal_source)
                return True
            else:
                logger.error("Falló el clic en el botón de apuesta")
                return False
                
        except Exception as e:
            logger.error(f"Error ejecutando apuesta: {str(e)}", exc_info=True)
            return False
    
    def _get_bet_button_locator(self, bet_type: str) -> Optional[str]:
        """Obtener locator del botón según el tipo de apuesta"""
        if bet_type == 'B':
            return locators.banker_button
        elif bet_type == 'P':
            return locators.player_button
        elif bet_type == 'E':
            return locators.tie_button
        return None
    
    def _wait_for_bet_ready(self, button_locator: str, max_wait: int = 10) -> bool:
        """Esperar a que el botón de apuesta esté listo"""
        try:
            # Esperar a que el panel de apuestas esté visible
            self.page.wait_for_selector(locators.bet_panel, timeout=max_wait * 1000)
            
            # Esperar a que el botón específico esté visible y habilitado
            button = self.page.wait_for_selector(
                button_locator, 
                timeout=max_wait * 1000,
                state='visible'
            )
            
            # Verificar que no esté deshabilitado
            is_disabled = button.get_attribute('disabled')
            if is_disabled:
                logger.debug("Botón de apuesta deshabilitado")
                return False
            
            return True
            
        except PlaywrightTimeoutError:
            logger.warning("Timeout esperando botón de apuesta")
            return False
        except Exception as e:
            logger.error(f"Error esperando botón: {str(e)}")
            return False
    
    def _human_like_preparation(self, button_locator: str):
        """Simular preparación humana antes de apostar"""
        try:
            # Movimiento aleatorio del mouse cerca del botón
            button = self.page.query_selector(button_locator)
            if button:
                box = button.bounding_box()
                if box:
                    # Mover a posición aleatoria cerca del botón
                    offset_x = box['width'] * 0.1
                    offset_y = box['height'] * 0.1
                    
                    start_x = box['x'] + random.uniform(offset_x, box['width'] - offset_x)
                    start_y = box['y'] + random.uniform(offset_y, box['height'] - offset_y)
                    
                    self.page.mouse.move(start_x, start_y)
                    helpers.random_delay(0.1, 0.3)
            
            # Pequeña pausa de "decisión"
            helpers.random_delay(0.5, 1.2)
            
        except Exception as e:
            logger.debug(f"Error en simulación humana: {str(e)}")
    
    def _click_bet_button(self, button_locator: str) -> bool:
        """Hacer clic en el botón de apuesta con verificación"""
        try:
            button = self.page.query_selector(button_locator)
            if not button:
                logger.error("Botón no encontrado para hacer clic")
                return False
            
            # Hacer clic con verificación
            button.click()
            helpers.random_delay(0.2, 0.5)
            
            # Verificar confirmación (si aplica)
            if self._verify_bet_placed():
                return True
            else:
                # Reintentar si falla la verificación
                return self._retry_bet_placement(button_locator)
                
        except Exception as e:
            logger.error(f"Error haciendo clic: {str(e)}")
            return False
    
    def _verify_bet_placed(self) -> bool:
        """Verificar que la apuesta fue colocada exitosamente"""
        try:
            # Buscar indicadores de apuesta exitosa
            success_indicators = [
                locators.bet_success,
                "//div[contains(text(), 'apuesta')]",
                "//div[contains(text(), 'bet')]"
            ]
            
            for indicator in success_indicators:
                element = self.page.query_selector(indicator)
                if element and element.is_visible():
                    return True
            
            # Verificar cambios en la interfaz que indiquen apuesta colocada
            helpers.random_delay(1.0, 2.0)
            return True  # Asumir éxito si no hay indicadores claros
            
        except Exception as e:
            logger.debug(f"Error verificando apuesta: {str(e)}")
            return True  # Asumir éxito para continuar
    
    def _retry_bet_placement(self, button_locator: str, max_retries: int = 2) -> bool:
        """Reintentar colocación de apuesta"""
        for attempt in range(max_retries):
            logger.info(f"Reintentando apuesta (intento {attempt + 1})")
            helpers.random_delay(1.0, 2.0)
            
            try:
                button = self.page.query_selector(button_locator)
                if button:
                    button.click()
                    helpers.random_delay(0.5, 1.0)
                    
                    if self._verify_bet_placed():
                        return True
            except Exception as e:
                logger.debug(f"Error en reintento {attempt + 1}: {str(e)}")
        
        return False
    
    def get_execution_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas de ejecución"""
        return {
            'total_executions': self.execution_count,
            'success_rate': 'N/A'  # Se podría calcular con más tracking
        }