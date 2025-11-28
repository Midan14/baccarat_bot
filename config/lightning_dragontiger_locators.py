# config/lightning_dragontiger_locators.py
"""
Locators específicos para Lightning Dragon Tiger de Evolution Gaming
"""

from typing import Dict

class LightningDragonTigerLocators:
    """Selectores CSS y XPath para Lightning Dragon Tiger"""
    
    # Área principal del juego
    GAME_CONTAINER = ".game-container"
    GAME_TABLE = ".game-table"
    DEALER_VIDEO = ".dealer-video"
    
    # Áreas de apuesta
    DRAGON_BET_AREA = ".bet-area[data-bet='dragon']"
    TIGER_BET_AREA = ".bet-area[data-bet='tiger']"
    TIE_BET_AREA = ".bet-area[data-bet='tie']"
    
    # Historial y estadísticas
    HISTORY_PANEL = ".history-panel"
    ROAD_MAP = ".road-map"
    BEAD_ROAD = ".bead-road"
    BIG_ROAD = ".big-road"
    BIG_EYE_ROAD = ".big-eye-road"
    SMALL_ROAD = ".small-road"
    COCKROACH_ROAD = ".cockroach-road"
    
    # Controles de apuesta
    CHIP_RACK = ".chip-rack"
    CHIP_SELECTOR = ".chip-selector"
    SELECTED_CHIP = ".chip-selector .selected"
    BET_BUTTONS = ".bet-buttons"
    PLACE_BET_BUTTON = ".place-bet-button"
    CLEAR_BET_BUTTON = ".clear-bet-button"
    REBET_BUTTON = ".rebet-button"
    DOUBLE_BUTTON = ".double-button"
    
    # Información del juego
    GAME_STATUS = ".game-status"
    BETTING_TIMER = ".betting-timer"
    TIME_REMAINING = ".time-remaining"
    ROUND_NUMBER = ".round-number"
    GAME_RESULT = ".game-result"
    
    # Displays de información
    BALANCE_DISPLAY = ".balance-display"
    TOTAL_BET_DISPLAY = ".total-bet-display"
    WIN_DISPLAY = ".win-display"
    LAST_WIN_DISPLAY = ".last-win-display"
    
    # Cartas y resultados
    DRAGON_CARD = ".dragon-card"
    TIGER_CARD = ".tiger-card"
    CARD_VALUE = ".card-value"
    CARD_SUIT = ".card-suit"
    
    # Multiplicadores Lightning
    LIGHTNING_MULTIPLIER = ".lightning-multiplier"
    LIGHTNING_NUMBERS = ".lightning-numbers"
    SELECTED_MULTIPLIERS = ".selected-multipliers"
    
    # Mensajes y notificaciones
    NOTIFICATION_AREA = ".notification-area"
    ERROR_MESSAGE = ".error-message"
    SUCCESS_MESSAGE = ".success-message"
    WARNING_MESSAGE = ".warning-message"
    
    # Configuración y opciones
    SETTINGS_BUTTON = ".settings-button"
    SOUND_TOGGLE = ".sound-toggle"
    VIDEO_QUALITY = ".video-quality"
    FULLSCREEN_BUTTON = ".fullscreen-button"
    
    # XPath alternativos para elementos difíciles de seleccionar
    XPATHS: Dict[str, str] = {
        "dragon_bet_button": "//div[contains(@class, 'bet-area') and contains(@data-bet, 'dragon')]//button[contains(@class, 'bet-button')]",
        "tiger_bet_button": "//div[contains(@class, 'bet-area') and contains(@data-bet, 'tiger')]//button[contains(@class, 'bet-button')]",
        "tie_bet_button": "//div[contains(@class, 'bet-area') and contains(@data-bet, 'tie')]//button[contains(@class, 'bet-button')]",
        "current_balance": "//div[contains(@class, 'balance-display')]//span[contains(@class, 'balance-amount')]",
        "betting_status": "//div[contains(@class, 'game-status')]//span[contains(@class, 'status-text')]",
        "time_remaining": "//div[contains(@class, 'betting-timer')]//span[contains(@class, 'time-remaining')]"
    }
    
    # Métodos de utilidad
    @staticmethod
    def get_bet_area(bet_type: str) -> str:
        """Obtener el selector del área de apuesta según el tipo"""
        bet_areas = {
            "dragon": LightningDragonTigerLocators.DRAGON_BET_AREA,
            "tiger": LightningDragonTigerLocators.TIGER_BET_AREA,
            "tie": LightningDragonTigerLocators.TIE_BET_AREA
        }
        return bet_areas.get(bet_type.lower(), "")
    
    @staticmethod
    def get_bet_button_xpath(bet_type: str) -> str:
        """Obtener el XPath del botón de apuesta según el tipo"""
        xpaths = {
            "dragon": LightningDragonTigerLocators.XPATHS["dragon_bet_button"],
            "tiger": LightningDragonTigerLocators.XPATHS["tiger_bet_button"],
            "tie": LightningDragonTigerLocators.XPATHS["tie_bet_button"]
        }
        return xpaths.get(bet_type.lower(), "")

# Instancia de locators
lightning_dragontiger_locators = LightningDragonTigerLocators()

# Variable global para compatibilidad con el código existente
locators = lightning_dragontiger_locators