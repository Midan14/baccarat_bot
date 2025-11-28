"""
Sistema avanzado de adquisición de datos en tiempo real
Captura datos de casinos en vivo vía APIs y WebSocket
"""

import asyncio
import aiohttp
import websocket
import json
import time
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
from datetime import datetime
import threading
import queue
import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

@dataclass
class GameData:
    """Estructura de datos de juego"""
    timestamp: datetime
    table_id: str
    round_number: int
    result: str  # B, P, T
    banker_cards: List[str]
    player_cards: List[str]
    banker_score: int
    player_score: int
    shoe_position: int
    dealer_name: str
    game_variant: str


class DataSource(ABC):
    """Interfaz base para fuentes de datos"""
    
    @abstractmethod
    async def connect(self):
        pass
    
    @abstractmethod
    async def disconnect(self):
        pass
    
    @abstractmethod
    async def get_game_data(self) -> Optional[GameData]:
        pass


class LiveCasinoAPI(DataSource):
    """Conexión a APIs de casinos en vivo"""
    
    def __init__(self, api_key: str, casino_id: str, base_url: str = None):
        self.api_key = api_key
        self.casino_id = casino_id
        self.base_url = base_url or "https://api.livecasino.com/v1"
        self.session = None
        self.connected = False
        
        # Configuración de reintento
        self.max_retries = 5
        self.retry_delay = 2
        
    async def connect(self):
        """Establece conexión con la API"""
        try:
            self.session = aiohttp.ClientSession(
                headers={
                    'Authorization': f'Bearer {self.api_key}',
                    'Content-Type': 'application/json',
                    'User-Agent': 'BaccaratBot/2.0'
                },
                timeout=aiohttp.ClientTimeout(total=30)
            )
            
            # Verificar conexión
            async with self.session.get(f"{self.base_url}/health") as response:
                if response.status == 200:
                    self.connected = True
                    logger.info("Conectado a API de casino en vivo")
                else:
                    raise ConnectionError(f"Error de conexión: {response.status}")
                    
        except Exception as e:
            logger.error(f"Error conectando a API: {e}")
            raise
    
    async def disconnect(self):
        """Cierra conexión con la API"""
        if self.session:
            await self.session.close()
            self.connected = False
            logger.info("Desconectado de API de casino")
    
    async def get_game_data(self) -> Optional[GameData]:
        """Obtiene datos de juego en tiempo real"""
        if not self.connected:
            await self.connect()
            
        for attempt in range(self.max_retries):
            try:
                async with self.session.get(f"{self.base_url}/games/live/baccarat") as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._parse_game_data(data)
                    elif response.status == 429:  # Rate limit
                        await asyncio.sleep(self.retry_delay * (attempt + 1))
                        continue
                    else:
                        logger.warning(f"Error API: {response.status}")
                        
            except Exception as e:
                logger.error(f"Error obteniendo datos: {e}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay)
                else:
                    return None
                    
        return None
    
    def _parse_game_data(self, raw_data: Dict) -> Optional[GameData]:
        """Parsea datos crudos a estructura GameData"""
        try:
            game_info = raw_data.get('game_info', {})
            result_info = raw_data.get('result', {})
            
            return GameData(
                timestamp=datetime.fromisoformat(game_info.get('timestamp', datetime.now().isoformat())),
                table_id=game_info.get('table_id', 'unknown'),
                round_number=game_info.get('round_number', 0),
                result=result_info.get('winner', 'B'),
                banker_cards=result_info.get('banker_cards', []),
                player_cards=result_info.get('player_cards', []),
                banker_score=result_info.get('banker_score', 0),
                player_score=result_info.get('player_score', 0),
                shoe_position=game_info.get('shoe_position', 0),
                dealer_name=game_info.get('dealer_name', 'Unknown'),
                game_variant=game_info.get('game_variant', 'standard')
            )
        except Exception as e:
            logger.error(f"Error parseando datos: {e}")
            return None


class WebSocketCasino(DataSource):
    """Conexión WebSocket para datos en tiempo real"""
    
    def __init__(self, ws_url: str, api_key: str):
        self.ws_url = ws_url
        self.api_key = api_key
        self.ws = None
        self.connected = False
        self.data_queue = queue.Queue(maxsize=1000)
        self.running = False
        
    async def connect(self):
        """Conecta vía WebSocket"""
        try:
            # WebSocket en un hilo separado
            self.running = True
            ws_thread = threading.Thread(target=self._ws_thread)
            ws_thread.daemon = True
            ws_thread.start()
            
            # Esperar conexión
            for _ in range(30):  # 30 segundos timeout
                if self.connected:
                    break
                await asyncio.sleep(1)
                
            if not self.connected:
                raise ConnectionError("No se pudo conectar vía WebSocket")
                
        except Exception as e:
            logger.error(f"Error conectando WebSocket: {e}")
            raise
    
    def _ws_thread(self):
        """Hilo de WebSocket para recibir datos"""
        def on_open(ws):
            logger.info("WebSocket conectado")
            self.connected = True
            # Enviar autenticación
            auth_msg = {
                'type': 'auth',
                'api_key': self.api_key,
                'subscribe': ['baccarat_results']
            }
            ws.send(json.dumps(auth_msg))
        
        def on_message(ws, message):
            try:
                data = json.loads(message)
                if data.get('type') == 'game_result':
                    game_data = self._parse_ws_data(data)
                    if game_data:
                        self.data_queue.put(game_data)
            except Exception as e:
                logger.error(f"Error procesando mensaje WebSocket: {e}")
        
        def on_error(ws, error):
            logger.error(f"Error WebSocket: {error}")
            self.connected = False
        
        def on_close(ws):
            logger.info("WebSocket desconectado")
            self.connected = False
        
        self.ws = websocket.WebSocketApp(
            self.ws_url,
            on_open=on_open,
            on_message=on_message,
            on_error=on_error,
            on_close=on_close
        )
        
        self.ws.run_forever()
    
    def _parse_ws_data(self, data: Dict) -> Optional[GameData]:
        """Parsea datos de WebSocket"""
        try:
            return GameData(
                timestamp=datetime.now(),
                table_id=data.get('table_id', 'live'),
                round_number=data.get('round_id', 0),
                result=data.get('result', 'B'),
                banker_cards=data.get('banker_cards', []),
                player_cards=data.get('player_cards', []),
                banker_score=data.get('banker_total', 0),
                player_score=data.get('player_total', 0),
                shoe_position=data.get('shoe_position', 0),
                dealer_name=data.get('dealer', 'Live'),
                game_variant=data.get('variant', 'live')
            )
        except Exception as e:
            logger.error(f"Error parseando datos WebSocket: {e}")
            return None
    
    async def disconnect(self):
        """Desconecta WebSocket"""
        self.running = False
        if self.ws:
            self.ws.close()
        self.connected = False
    
    async def get_game_data(self) -> Optional[GameData]:
        """Obtiene datos de la cola"""
        try:
            # Timeout de 1 segundo para no bloquear
            return self.data_queue.get(timeout=1)
        except queue.Empty:
            return None


class DataAggregator:
    """Agrega datos de múltiples fuentes"""
    
    def __init__(self):
        self.sources: List[DataSource] = []
        self.data_buffer: List[GameData] = []
        self.max_buffer_size = 1000
        self.callbacks: List[Callable] = []
        
    def add_source(self, source: DataSource):
        """Agrega fuente de datos"""
        self.sources.append(source)
        
    def add_callback(self, callback: Callable[[GameData], None]):
        """Agrega callback para nuevos datos"""
        self.callbacks.append(callback)
        
    async def start_collection(self):
        """Inicia recolección de datos"""
        tasks = []
        for source in self.sources:
            task = asyncio.create_task(self._collect_from_source(source))
            tasks.append(task)
            
        await asyncio.gather(*tasks)
    
    async def _collect_from_source(self, source: DataSource):
        """Recoge datos de una fuente específica"""
        await source.connect()
        
        while True:
            try:
                data = await source.get_game_data()
                if data:
                    self._process_new_data(data)
                await asyncio.sleep(0.1)  # 100ms entre consultas
                
            except Exception as e:
                logger.error(f"Error recogiendo datos: {e}")
                await asyncio.sleep(5)  # Esperar antes de reintentar
    
    def _process_new_data(self, data: GameData):
        """Procesa nuevo dato de juego"""
        # Agregar al buffer
        self.data_buffer.append(data)
        if len(self.data_buffer) > self.max_buffer_size:
            self.data_buffer.pop(0)
            
        # Llamar callbacks
        for callback in self.callbacks:
            try:
                callback(data)
            except Exception as e:
                logger.error(f"Error en callback: {e}")
    
    def get_recent_data(self, count: int = 100) -> List[GameData]:
        """Obtiene datos recientes"""
        return self.data_buffer[-count:]
    
    def get_statistics(self) -> Dict:
        """Obtiene estadísticas de los datos"""
        if not self.data_buffer:
            return {}
            
        results = [d.result for d in self.data_buffer]
        
        return {
            'total_hands': len(results),
            'banker_percentage': results.count('B') / len(results),
            'player_percentage': results.count('P') / len(results),
            'tie_percentage': results.count('T') / len(results),
            'tables_played': len(set(d.table_id for d in self.data_buffer)),
            'time_range': {
                'start': min(d.timestamp for d in self.data_buffer),
                'end': max(d.timestamp for d in self.data_buffer)
            }
        }


class DataValidator:
    """Valida integridad de datos"""
    
    @staticmethod
    def validate_game_data(data: GameData) -> bool:
        """Valida datos de juego"""
        try:
            # Validar timestamp
            if not isinstance(data.timestamp, datetime):
                return False
                
            # Validar resultado
            if data.result not in ['B', 'P', 'T']:
                return False
                
            # Validar puntuaciones
            if not (0 <= data.banker_score <= 9 and 0 <= data.player_score <= 9):
                return False
                
            # Validar cartas
            valid_cards = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
            for card in data.banker_cards + data.player_cards:
                if card not in valid_cards:
                    return False
                    
            # Validar posición en zapato
            if not (0 <= data.shoe_position <= 80):
                return False
                
            return True
            
        except Exception:
            return False
    
    @staticmethod
    def cross_validate_data(sources_data: List[Optional[GameData]]) -> Optional[GameData]:
        """Validación cruzada entre múltiples fuentes"""
        valid_data = [d for d in sources_data if d and DataValidator.validate_game_data(d)]
        
        if not valid_data:
            return None
            
        # Si hay discrepancias, usar la mayoría
        if len(valid_data) > 1:
            results = [d.result for d in valid_data]
            most_common = max(set(results), key=results.count)
            
            # Usar el dato más reciente con el resultado mayoritario
            for d in sorted(valid_data, key=lambda x: x.timestamp, reverse=True):
                if d.result == most_common:
                    return d
                    
        return valid_data[0]


# Configuración de APIs de casinos populares
CASINO_APIS = {
    'evolution_gaming': {
        'base_url': 'https://api.evolutiongaming.com/live/v2',
        'websocket': 'wss://live.evolutiongaming.com/stream',
        'requires_key': True
    },
    'pragmatic_play': {
        'base_url': 'https://api.pragmaticplay.com/live/v1',
        'websocket': 'wss://live.pragmaticplay.com/ws',
        'requires_key': True
    },
    'playtech': {
        'base_url': 'https://api.playtech.com/live/v3',
        'websocket': 'wss://live.playtech.com/stream',
        'requires_key': True
    },
    'betconstruct': {
        'base_url': 'https://api.betconstruct.com/live/v1',
        'websocket': 'wss://live.betconstruct.com/ws',
        'requires_key': True
    }
}


def create_casino_connection(casino_name: str, api_key: str) -> DataSource:
    """Crea conexión para casino específico"""
    
    if casino_name not in CASINO_APIS:
        raise ValueError(f"Casino no soportado: {casino_name}")
        
    config = CASINO_APIS[casino_name]
    
    # Crear API connection
    api_connection = LiveCasinoAPI(
        api_key=api_key,
        casino_id=casino_name,
        base_url=config['base_url']
    )
    
    # Crear WebSocket connection
    ws_connection = WebSocketCasino(
        ws_url=config['websocket'],
        api_key=api_key
    )
    
    return api_connection  # Por ahora, usar solo API