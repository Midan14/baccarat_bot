# core/aggressive_data_acquisition.py
"""
Sistema agresivo de adquisición de datos en tiempo real
"""

import time
import json
import re
from typing import List, Dict, Any, Optional
from playwright.sync_api import Page, BrowserContext
from config.settings import settings
from utils.logger import logger
from utils.helpers import helpers

class AggressiveDataAcquisition:
    """Sistema agresivo de scraping de datos"""
    
    def __init__(self, page: Page, context: BrowserContext):
        self.page = page
        self.context = context
        self.current_history_hash = None
        self.last_update_time = 0
        self.update_interval = 1.0  # Actualizar cada segundo
        self.max_retries = 5
        self.retry_delay = 0.5
        
    def aggressive_wait_for_game(self, timeout: int = 30000) -> bool:
        """Espera agresiva para que el juego cargue"""
        try:
            logger.info("🔍 Iniciando espera agresiva para carga del juego...")
            
            # Múltiples estrategias de espera
            strategies = [
                self._wait_by_selectors,
                self._wait_by_network,
                self._wait_by_content,
                self._wait_by_elements
            ]
            
            for strategy in strategies:
                try:
                    if strategy(timeout // len(strategies)):
                        logger.info("✅ Juego detectado exitosamente")
                        return True
                except Exception as e:
                    logger.debug(f"Estrategia fallida: {str(e)}")
                    continue
            
            logger.warning("⚠️ No se pudo detectar el juego con ninguna estrategia")
            return False
            
        except Exception as e:
            logger.error(f"❌ Error en espera agresiva: {str(e)}")
            return False
    
    def _wait_by_selectors(self, timeout: int) -> bool:
        """Esperar por selectores CSS específicos"""
        selectors = [
            ".game-area", ".history-panel", ".results-container",
            ".dragontiger-history", ".evolution-history", ".live-casino-history",
            "[data-game='dragontiger']", "[data-provider='evolution']"
        ]
        
        for selector in selectors:
            try:
                self.page.wait_for_selector(selector, timeout=timeout//len(selectors))
                logger.info(f"✅ Selector encontrado: {selector}")
                return True
            except:
                continue
        
        return False
    
    def _wait_by_network(self, timeout: int) -> bool:
        """Esperar por peticiones de red específicas"""
        try:
            # Interceptar peticiones de red
            responses = []
            
            def handle_response(response):
                url = response.url.lower()
                if any(keyword in url for keyword in ['history', 'results', 'game', 'round']):
                    responses.append(response)
            
            self.page.on("response", handle_response)
            
            # Esperar un momento para capturar respuestas
            time.sleep(2)
            
            if responses:
                logger.info(f"✅ Capturadas {len(responses)} respuestas de red")
                return True
            
            return False
            
        except Exception as e:
            logger.debug(f"Error en espera por red: {str(e)}")
            return False
    
    def _wait_by_content(self, timeout: int) -> bool:
        """Esperar por contenido específico en la página"""
        keywords = ['dragon', 'tiger', 'tie', 'history', 'results', 'round']
        
        for keyword in keywords:
            try:
                if self.page.content().lower().count(keyword) > 2:
                    logger.info(f"✅ Contenido detectado: {keyword}")
                    return True
            except:
                continue
        
        return False
    
    def _wait_by_elements(self, timeout: int) -> bool:
        """Buscar elementos por múltiples estrategias"""
        element_selectors = [
            "//*[contains(@class, 'history')]",
            "//*[contains(@class, 'result')]",
            "//*[contains(@class, 'dragon')]",
            "//*[contains(@class, 'tiger')]",
            "//*[contains(text(), 'Dragon')]",
            "//*[contains(text(), 'Tiger')]",
            "//*[contains(text(), 'Tie')]"
        ]
        
        for xpath in element_selectors:
            try:
                elements = self.page.query_selector_all(f"xpath={xpath}")
                if elements:
                    logger.info(f"✅ Elementos encontrados con: {xpath}")
                    return True
            except:
                continue
        
        return False
    
    def aggressive_extract_history(self) -> Optional[List[str]]:
        """Extracción agresiva del historial"""
        try:
            # Verificar si es momento de actualizar
            current_time = time.time()
            if current_time - self.last_update_time < self.update_interval:
                return None
            
            self.last_update_time = current_time
            
            # Múltiples estrategias de extracción
            extraction_methods = [
                self._extract_by_css_selectors,
                self._extract_by_xpath,
                self._extract_by_text_content,
                self._extract_by_attributes,
                self._extract_by_javascript
            ]
            
            for method in extraction_methods:
                try:
                    history = method()
                    if history and len(history) > 0:
                        if self._validate_and_update_history(history):
                            logger.info(f"✅ Historial extraído con {method.__name__}: {len(history)} resultados")
                            return history
                except Exception as e:
                    logger.debug(f"Método {method.__name__} falló: {str(e)}")
                    continue
            
            logger.warning("⚠️ No se pudo extraer historial con ningún método")
            return None
            
        except Exception as e:
            logger.error(f"❌ Error en extracción agresiva: {str(e)}")
            return None
    
    def _extract_by_css_selectors(self) -> Optional[List[str]]:
        """Extraer por selectores CSS"""
        selectors = [
            ".history-item", ".result-item", ".round-result",
            ".dragon-result", ".tiger-result", ".tie-result",
            ".history-cell", ".result-cell", ".game-result"
        ]
        
        for selector in selectors:
            elements = self.page.query_selector_all(selector)
            if elements:
                history = []
                for element in elements[:50]:  # Limitar a últimos 50
                    result = self._parse_result_element(element)
                    if result:
                        history.append(result)
                return history if history else None
        
        return None
    
    def _extract_by_xpath(self) -> Optional[List[str]]:
        """Extraer por XPath"""
        xpaths = [
            "//*[contains(@class, 'history')]//*[contains(@class, 'result')]",
            "//*[contains(@class, 'result') and (contains(text(), 'D') or contains(text(), 'T') or contains(text(), 'E'))]",
            "//*[contains(@class, 'dragon') or contains(@class, 'tiger') or contains(@class, 'tie')]",
            "//*[contains(text(), 'Dragon') or contains(text(), 'Tiger') or contains(text(), 'Tie')]"
        ]
        
        for xpath in xpaths:
            elements = self.page.query_selector_all(f"xpath={xpath}")
            if elements:
                history = []
                for element in elements[:50]:
                    result = self._parse_result_element(element)
                    if result:
                        history.append(result)
                return history if history else None
        
        return None
    
    def _extract_by_text_content(self) -> Optional[List[str]]:
        """Extraer por análisis de texto"""
        try:
            content = self.page.text_content()
            # Buscar patrones de resultados
            patterns = [
                r'Dragon|Tiger|Tie',
                r'[DT]\d+',  # D1, T2, etc.
                r'[RGB]',    # Rojo, Verde, Azul
                r'BANKER|PLAYER|TIE'
            ]
            
            history = []
            for pattern in patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    # Convertir a formato estándar
                    for match in matches:
                        match = match.upper()
                        if match in ['DRAGON', 'D', 'ROJO', 'RED', 'BANKER']:
                            history.append('B')
                        elif match in ['TIGER', 'T', 'AZUL', 'BLUE', 'PLAYER']:
                            history.append('P')
                        elif match in ['TIE', 'E', 'VERDE', 'GREEN', 'EMPATE']:
                            history.append('E')
                    
                    if history:
                        return history
            
            return None
            
        except Exception as e:
            logger.debug(f"Error en extracción por texto: {str(e)}")
            return None
    
    def _extract_by_attributes(self) -> Optional[List[str]]:
        """Extraer por atributos de elementos"""
        try:
            # Buscar elementos con atributos específicos
            attributes = ['data-result', 'data-outcome', 'data-value', 'result']
            
            for attr in attributes:
                elements = self.page.query_selector_all(f"[{attr}]")
                if elements:
                    history = []
                    for element in elements[:50]:
                        value = element.get_attribute(attr)
                        if value:
                            result = self._parse_result_value(value)
                            if result:
                                history.append(result)
                    return history if history else None
            
            return None
            
        except Exception as e:
            logger.debug(f"Error en extracción por atributos: {str(e)}")
            return None
    
    def _extract_by_javascript(self) -> Optional[List[str]]:
        """Extraer ejecutando JavaScript"""
        try:
            # Intentar acceder a variables JavaScript
            scripts = [
                "return window.gameHistory || window.history || [];",
                "return Array.from(document.querySelectorAll('.result')).map(el => el.textContent);",
                "return Array.from(document.querySelectorAll('[data-result]')).map(el => el.dataset.result);",
                "return window.localStorage.getItem('gameHistory') ? JSON.parse(window.localStorage.getItem('gameHistory')) : [];"
            ]
            
            for script in scripts:
                try:
                    result = self.page.evaluate(script)
                    if result and isinstance(result, list):
                        history = []
                        for item in result[:50]:
                            parsed = self._parse_result_value(str(item))
                            if parsed:
                                history.append(parsed)
                        return history if history else None
                except:
                    continue
            
            return None
            
        except Exception as e:
            logger.debug(f"Error en extracción por JavaScript: {str(e)}")
            return None
    
    def _parse_result_element(self, element) -> Optional[str]:
        """Parsear elemento individual del resultado (versión mejorada)"""
        try:
            # Método 1: Por clase CSS
            class_name = element.get_attribute('class') or ''
            class_lower = class_name.lower()
            
            if any(word in class_lower for word in ['dragon', 'banker', 'rojo', 'red', 'b']):
                return 'B'
            elif any(word in class_lower for word in ['tiger', 'player', 'azul', 'blue', 'p']):
                return 'P'
            elif any(word in class_lower for word in ['tie', 'empate', 'verde', 'green', 'e']):
                return 'E'
            
            # Método 2: Por texto
            text_content = element.text_content() or ''
            text_upper = text_content.upper()
            
            if any(char in text_upper for char in ['D', 'B', 'R']):
                return 'B'
            elif any(char in text_upper for char in ['T', 'P', 'A']):
                return 'P'
            elif any(char in text_upper for char in ['E', 'V', 'X']):
                return 'E'
            
            # Método 3: Por atributos
            for attr in ['data-result', 'data-outcome', 'data-value']:
                value = element.get_attribute(attr)
                if value:
                    parsed = self._parse_result_value(value)
                    if parsed:
                        return parsed
            
            return None
            
        except Exception as e:
            logger.debug(f"Error parseando elemento: {str(e)}")
            return None
    
    def _parse_result_value(self, value: str) -> Optional[str]:
        """Parsear valor de resultado"""
        value_upper = value.upper().strip()
        
        if value_upper in ['DRAGON', 'D', 'BANKER', 'B', 'ROJO', 'RED', 'R']:
            return 'B'
        elif value_upper in ['TIGER', 'T', 'PLAYER', 'P', 'AZUL', 'BLUE', 'A']:
            return 'P'
        elif value_upper in ['TIE', 'E', 'EMPATE', 'VERDE', 'GREEN', 'V', 'X']:
            return 'E'
        
        return None
    
    def _validate_and_update_history(self, history: List[str]) -> bool:
        """Validar historial y detectar cambios"""
        if not history or len(history) < 1:
            return False
        
        # Validar que todos los elementos sean válidos
        valid_results = ['B', 'P', 'E']
        if not all(result in valid_results for result in history):
            return False
        
        # Detectar cambios
        current_hash = helpers.calculate_hash(str(history))
        
        if current_hash != self.current_history_hash:
            self.current_history_hash = current_hash
            return True
        
        return False  # Sin cambios
    
    def get_game_state_aggressive(self) -> Dict[str, Any]:
        """Obtener estado completo del juego con scraping agresivo"""
        try:
            # Extraer historial con método agresivo
            history = self.aggressive_extract_history()
            
            state = {
                'history': history or [],
                'timestamp': helpers.get_timestamp(),
                'current_hand': self._get_current_hand(),
                'time_remaining': self._get_time_remaining(),
                'betting_open': self._is_betting_open(),
                'scraping_method': 'aggressive',
                'update_interval': self.update_interval
            }
            
            # Si no hay historial, intentar extraer con métodos alternativos
            if not history:
                logger.warning("⚠️ No se pudo extraer historial, intentando métodos alternativos")
                state['history'] = self._emergency_extraction()
            
            return state
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo estado agresivo: {str(e)}")
            return {'history': [], 'error': str(e)}
    
    def _emergency_extraction(self) -> List[str]:
        """Extracción de emergencia cuando todos los métodos fallan"""
        try:
            # Último recurso: buscar cualquier elemento que pueda contener resultados
            all_elements = self.page.query_selector_all("*")
            
            emergency_history = []
            for element in all_elements[:100]:  # Limitar búsqueda
                try:
                    text = element.text_content()
                    if text and len(text) <= 10:  # Textos cortos
                        result = self._parse_result_value(text)
                        if result:
                            emergency_history.append(result)
                except:
                    continue
            
            return emergency_history[:20]  # Limitar resultados
            
        except Exception as e:
            logger.error(f"Error en extracción de emergencia: {str(e)}")
            return []
    
    def _get_current_hand(self) -> Optional[str]:
        """Obtener número de mano actual (versión mejorada)"""
        try:
            # Múltiples selectores para mano actual
            selectors = [
                locators.current_hand,
                ".current-hand", ".hand-number", ".round-number",
                "[data-hand]", "[data-round]"
            ]
            
            for selector in selectors:
                try:
                    element = self.page.query_selector(selector)
                    if element:
                        return element.text_content().strip()
                except:
                    continue
            
            return None
            
        except Exception as e:
            logger.debug(f"Error obteniendo mano actual: {str(e)}")
            return None
    
    def _get_time_remaining(self) -> Optional[str]:
        """Obtener tiempo restante (versión mejorada)"""
        try:
            # Múltiples selectores para tiempo
            selectors = [
                locators.timer,
                ".timer", ".countdown", ".time-remaining",
                "[data-time]", "[data-countdown]"
            ]
            
            for selector in selectors:
                try:
                    element = self.page.query_selector(selector)
                    if element:
                        return element.text_content().strip()
                except:
                    continue
            
            return None
            
        except Exception as e:
            logger.debug(f"Error obteniendo tiempo restante: {str(e)}")
            return None
    
    def _is_betting_open(self) -> bool:
        """Verificar si la apuesta está abierta (versión mejorada)"""
        try:
            # Múltiples estrategias para verificar estado
            strategies = [
                self._check_by_status_element,
                self._check_by_button_state,
                self._check_by_timer,
                self._check_by_class_names
            ]
            
            for strategy in strategies:
                try:
                    result = strategy()
                    if result is not None:
                        return result
                except:
                    continue
            
            return True  # Asumir abierto por defecto
            
        except Exception as e:
            logger.debug(f"Error verificando estado de apuesta: {str(e)}")
            return True
    
    def _check_by_status_element(self) -> Optional[bool]:
        """Verificar por elemento de estado"""
        status_selectors = [
            locators.game_status,
            ".game-status", ".betting-status", ".round-status"
        ]
        
        for selector in status_selectors:
            element = self.page.query_selector(selector)
            if element:
                status_text = element.text_content().lower()
                if any(word in status_text for word in ['apuesta', 'betting', 'open', 'active']):
                    return True
                elif any(word in status_text for word in ['closed', 'waiting', 'result']):
                    return False
        
        return None
    
    def _check_by_button_state(self) -> Optional[bool]:
        """Verificar por estado de botones"""
        button_selectors = [
            ".place-bet-button", ".bet-button", ".confirm-bet",
            "[data-action='place-bet']", "[data-bet='place']"
        ]
        
        for selector in button_selectors:
            element = self.page.query_selector(selector)
            if element:
                # Verificar si el botón está habilitado
                is_disabled = element.get_attribute('disabled') is not None
                is_hidden = element.get_attribute('hidden') is not None
                has_disabled_class = 'disabled' in (element.get_attribute('class') or '')
                
                return not (is_disabled or is_hidden or has_disabled_class)
        
        return None
    
    def _check_by_timer(self) -> Optional[bool]:
        """Verificar por tiempo restante"""
        time_remaining = self._get_time_remaining()
        if time_remaining:
            # Si hay tiempo mostrado, asumir que la apuesta está abierta
            return True
        
        return None
    
    def _check_by_class_names(self) -> Optional[bool]:
        """Verificar por clases CSS"""
        open_indicators = ['open', 'active', 'betting', 'available']
        closed_indicators = ['closed', 'inactive', 'waiting', 'result']
        
        all_elements = self.page.query_selector_all("*")
        
        for element in all_elements[:50]:  # Limitar búsqueda
            class_name = element.get_attribute('class') or ''
            class_lower = class_name.lower()
            
            if any(indicator in class_lower for indicator in open_indicators):
                return True
            elif any(indicator in class_lower for indicator in closed_indicators):
                return False
        
        return None