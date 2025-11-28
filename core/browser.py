# core/browser.py
from playwright.sync_api import sync_playwright, Page, Browser, BrowserContext
from typing import Tuple, Optional
from config.settings import settings
from utils.logger import logger
from utils.helpers import helpers

class StealthBrowser:
    """Manejador robusto del navegador con técnicas anti-detección"""
    
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
    
    def start(self) -> Tuple[Page, Browser]:
        """Inicializar el navegador en modo stealth"""
        try:
            logger.info("Iniciando navegador en modo stealth...")
            self.playwright = sync_playwright().start()
            
            # Configurar opciones de lanzamiento
            launch_options = {
                'headless': settings.browser.headless,
                'args': [
                    '--no-sandbox',
                    '--disable-blink-features=AutomationControlled',
                    '--disable-features=VizDisplayCompositor',
                    '--disable-background-timer-throttling',
                    '--disable-backgrounding-occluded-windows',
                    '--disable-renderer-backgrounding',
                ]
            }
            
            self.browser = self.playwright.chromium.launch(**launch_options)
            
            # Configurar contexto
            context_options = {
                'user_agent': settings.browser.user_agent,
                'viewport': {'width': settings.browser.viewport_width, 
                           'height': settings.browser.viewport_height},
                'ignore_https_errors': True
            }
            
            self.context = self.browser.new_context(**context_options)
            
            if settings.browser.stealth_mode:
                self._apply_stealth_techniques()
            
            self.page = self.context.new_page()
            self.page.set_default_timeout(settings.browser.timeout)
            
            logger.info("Navegador iniciado exitosamente")
            return self.page, self.browser
            
        except Exception as e:
            logger.error(f"Error al iniciar el navegador: {str(e)}", exc_info=True)
            self.stop()
            raise
    
    def _apply_stealth_techniques(self):
        """Aplicar técnicas anti-detección"""
        stealth_script = """
        () => {
            // Eliminar webdriver property
            delete navigator.__proto__.webdriver;
            
            // Sobrescribir plugins
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5],
            });
            
            // Sobrescribir languages
            Object.defineProperty(navigator, 'languages', {
                get: () => ['es-ES', 'es', 'en-US', 'en'],
            });
            
            // Mock WebGL
            const canvas = document.createElement('canvas');
            const gl = canvas.getContext('webgl');
            const debugInfo = gl.getExtension('WEBGL_debug_renderer_info');
            if (debugInfo) {
                Object.defineProperty(gl.getParameter(debugInfo.UNMASKED_RENDERER_WEBGL), {
                    get: () => 'Intel Inc.',
                });
            }
            
            console.log('Stealth mode activated');
        }
        """
        self.context.add_init_script(stealth_script)
    
    def take_screenshot(self, name: str):
        """Tomar captura de pantalla para debugging"""
        try:
            screenshot_path = f"{settings.screenshots_dir}/{name}_{helpers.get_timestamp().replace(':', '-')}.png"
            self.page.screenshot(path=screenshot_path)
            logger.info(f"Captura guardada: {screenshot_path}")
        except Exception as e:
            logger.warning(f"No se pudo tomar captura: {str(e)}")
    
    def stop(self):
        """Cerrar el navegador y liberar recursos"""
        try:
            if self.browser:
                self.browser.close()
            if self.playwright:
                self.playwright.stop()
            logger.info("Navegador cerrado exitosamente")
        except Exception as e:
            logger.error(f"Error al cerrar el navegador: {str(e)}")