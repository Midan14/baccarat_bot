#!/usr/bin/env python3
"""
Generador de datos de demostración para Baccarat
Simula partidas en tiempo real para probar el bot
"""

import asyncio
import random
import time
from datetime import datetime
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

class DemoDataGenerator:
    """Genera datos de baccarat simulados para demostración"""
    
    def __init__(self):
        self.running = False
        self.game_history = []
        self.pattern_sequences = {
            'B': [0.45, 0.48, 0.46, 0.47, 0.49],  # Banker tiende a ganar más
            'P': [0.44, 0.43, 0.45, 0.44, 0.43],  # Player tiene menos probabilidad
            'T': [0.11, 0.09, 0.09, 0.09, 0.08]   # Tie es raro
        }
        
    async def start_generation(self):
        """Inicia la generación de datos de demostración"""
        logger.info("🎮 Iniciando generador de datos de demostración...")
        self.running = True
        
        while self.running:
            try:
                # Generar una partida simulada
                game_data = self._generate_game()
                self.game_history.append(game_data)
                
                # Mantener solo últimas 100 partidas
                if len(self.game_history) > 100:
                    self.game_history.pop(0)
                
                logger.info(f"🎲 Demo: {game_data['result']} | B:{game_data['banker_score']} P:{game_data['player_score']} | Mesa:{game_data['table_id']}")
                
                # Esperar 2-5 segundos para siguiente partida
                await asyncio.sleep(random.uniform(2, 5))
                
            except Exception as e:
                logger.error(f"Error en generador demo: {e}")
                await asyncio.sleep(1)
    
    def _generate_game(self) -> Dict:
        """Genera una partida de baccarat simulada"""
        # Generar scores basados en probabilidades reales
        banker_score = self._generate_score()
        player_score = self._generate_score()
        
        # Determinar ganador basado en reglas de baccarat
        result = self._determine_winner(banker_score, player_score)
        
        # Generar información adicional
        game_data = {
            'timestamp': datetime.now(),
            'table_id': f"DEMO_{random.randint(1, 5)}",
            'result': result,
            'banker_score': banker_score,
            'player_score': player_score,
            'banker_cards': self._generate_cards(banker_score),
            'player_cards': self._generate_cards(player_score),
            'shoe_number': random.randint(1, 8),
            'hand_number': len(self.game_history) + 1,
            'casino_name': random.choice(['Evolution Demo', 'Pragmatic Demo']),
            'dealer_name': random.choice(['Anna', 'Maria', 'John', 'David'])
        }
        
        return game_data
    
    def _generate_score(self) -> int:
        """Genera un score realista para baccarat (0-9)"""
        # Distribución más realista - tiende a scores medios
        scores = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
        weights = [0.05, 0.08, 0.10, 0.12, 0.15, 0.18, 0.15, 0.10, 0.05, 0.02]
        return random.choices(scores, weights=weights)[0]
    
    def _determine_winner(self, banker_score: int, player_score: int) -> str:
        """Determina el ganador según reglas de baccarat"""
        if banker_score > player_score:
            return 'B'
        elif player_score > banker_score:
            return 'P'
        else:
            return 'T'
    
    def _generate_cards(self, score: int) -> List[str]:
        """Genera cartas que sumen el score dado"""
        # Simplificación: generar 2-3 cartas que sumen el score
        cards = []
        remaining = score
        
        # Primera carta
        card1 = min(remaining, random.randint(0, 9))
        cards.append(self._card_to_string(card1))
        remaining -= card1
        
        if remaining > 0:
            card2 = min(remaining, random.randint(0, 9))
            cards.append(self._card_to_string(card2))
            remaining -= card2
            
            if remaining > 0:
                card3 = remaining
                cards.append(self._card_to_string(card3))
        
        return cards
    
    def _card_to_string(self, value: int) -> str:
        """Convierte valor de carta a string"""
        if value == 0:
            return "10♦"  # 10 vale 0 en baccarat
        elif value == 1:
            return "A♠"
        elif value < 10:
            suits = ['♠', '♥', '♦', '♣']
            return f"{value}{random.choice(suits)}"
        else:
            faces = ['J', 'Q', 'K']
            suits = ['♠', '♥', '♦', '♣']
            return f"{random.choice(faces)}{random.choice(suits)}"
    
    def get_recent_games(self, count: int = 10) -> List[Dict]:
        """Obtiene las partidas más recientes"""
        return self.game_history[-count:] if self.game_history else []
    
    def get_statistics(self) -> Dict:
        """Obtiene estadísticas de las partidas generadas"""
        if not self.game_history:
            return {
                'total_hands': 0,
                'banker_wins': 0,
                'player_wins': 0,
                'tie_wins': 0,
                'banker_percentage': 0,
                'player_percentage': 0,
                'tie_percentage': 0
            }
        
        total = len(self.game_history)
        banker_wins = sum(1 for game in self.game_history if game['result'] == 'B')
        player_wins = sum(1 for game in self.game_history if game['result'] == 'P')
        tie_wins = sum(1 for game in self.game_history if game['result'] == 'T')
        
        return {
            'total_hands': total,
            'banker_wins': banker_wins,
            'player_wins': player_wins,
            'tie_wins': tie_wins,
            'banker_percentage': banker_wins / total * 100,
            'player_percentage': player_wins / total * 100,
            'tie_percentage': tie_wins / total * 100,
            'tables_played': len(set(game['table_id'] for game in self.game_history))
        }
    
    def stop(self):
        """Detiene el generador"""
        self.running = False
        logger.info("🛑 Generador de datos de demostración detenido")


# Función principal para prueba independiente
async def main():
    """Prueba del generador de datos de demostración"""
    generator = DemoDataGenerator()
    
    print("🎮 Iniciando generador de datos de demostración...")
    print("Presiona Ctrl+C para detener")
    
    try:
        await generator.start_generation()
    except KeyboardInterrupt:
        print("\n🛑 Deteniendo generador...")
        generator.stop()


if __name__ == "__main__":
    asyncio.run(main())