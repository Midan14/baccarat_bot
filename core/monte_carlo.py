"""
Motor Monte Carlo para simulaciones probabilísticas avanzadas
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Tuple, Optional
import random
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import multiprocessing
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class MonteCarloEngine:
    """Motor principal para simulaciones Monte Carlo"""
    
    def __init__(self, num_simulations: int = 100000, num_decks: int = 8):
        self.num_simulations = num_simulations
        self.num_decks = num_decks
        self.cards_per_deck = 52
        self.total_cards = num_decks * self.cards_per_deck
        
        # Probabilidades base de baccarat
        self.base_probabilities = {
            'B': 0.4584,  # Banker
            'P': 0.4461,  # Player
            'T': 0.0955   # Tie
        }
        
    def simulate_shoe(self, current_state: Dict, num_hands: int = 10) -> Dict:
        """Simula el resto del zapato basado en estado actual"""
        
        # Extraer cartas conocidas
        known_cards = self._extract_known_cards(current_state)
        remaining_cards = self._calculate_remaining_cards(known_cards)
        
        # Realizar simulaciones
        results = self._run_simulations(remaining_cards, num_hands)
        
        # Analizar resultados
        analysis = self._analyze_simulation_results(results)
        
        return {
            'simulation_results': results,
            'probability_adjustments': analysis,
            'confidence_intervals': self._calculate_confidence_intervals(results),
            'expected_value': self._calculate_expected_value(analysis)
        }
    
    def _extract_known_cards(self, current_state: Dict) -> Dict:
        """Extrae cartas conocidas del estado actual"""
        known_cards = {
            'A': 0, '2': 0, '3': 0, '4': 0, '5': 0, '6': 0, '7': 0, '8': 0, '9': 0, '10': 0, 'J': 0, 'Q': 0, 'K': 0
        }
        
        # Contar cartas del historial
        if 'history' in current_state:
            for hand in current_state['history']:
                for card in hand.get('banker_cards', []) + hand.get('player_cards', []):
                    card_value = self._get_card_value(card)
                    if card_value in known_cards:
                        known_cards[card_value] += 1
                        
        return known_cards
    
    def _calculate_remaining_cards(self, known_cards: Dict) -> Dict:
        """Calcula cartas restantes en el zapato"""
        total_each_card = self.num_decks * 4  # 4 de cada carta por mazo
        remaining = {}
        
        for card, count in known_cards.items():
            remaining[card] = total_each_card - count
            
        return remaining
    
    def _run_simulations(self, remaining_cards: Dict, num_hands: int) -> List[Dict]:
        """Ejecuta simulaciones Monte Carlo"""
        
        def single_simulation():
            # Crear zapato simulado
            shoe = self._create_shoe_from_remaining(remaining_cards)
            random.shuffle(shoe)
            
            results = []
            for _ in range(num_hands):
                result = self._simulate_single_hand(shoe)
                results.append(result)
                
            return results
        
        # Ejecutar simulaciones en paralelo
        num_cores = multiprocessing.cpu_count()
        simulations_per_core = self.num_simulations // num_cores
        
        with ProcessPoolExecutor(max_workers=num_cores) as executor:
            futures = []
            for _ in range(num_cores):
                future = executor.submit(self._run_batch_simulations, 
                                       remaining_cards, num_hands, simulations_per_core)
                futures.append(future)
                
            all_results = []
            for future in futures:
                all_results.extend(future.result())
                
        return all_results
    
    def _run_batch_simulations(self, remaining_cards: Dict, num_hands: int, batch_size: int) -> List[Dict]:
        """Ejecuta un lote de simulaciones"""
        batch_results = []
        
        for _ in range(batch_size):
            shoe = self._create_shoe_from_remaining(remaining_cards)
            random.shuffle(shoe)
            
            simulation_result = {
                'hands': [],
                'total_banker_wins': 0,
                'total_player_wins': 0,
                'total_ties': 0
            }
            
            for _ in range(num_hands):
                hand_result = self._simulate_single_hand(shoe)
                simulation_result['hands'].append(hand_result)
                
                if hand_result['winner'] == 'B':
                    simulation_result['total_banker_wins'] += 1
                elif hand_result['winner'] == 'P':
                    simulation_result['total_player_wins'] += 1
                else:
                    simulation_result['total_ties'] += 1
                    
            batch_results.append(simulation_result)
            
        return batch_results
    
    def _create_shoe_from_remaining(self, remaining_cards: Dict) -> List[int]:
        """Crea zapato desde cartas restantes"""
        shoe = []
        card_values = {'A': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, 
                      '10': 0, 'J': 0, 'Q': 0, 'K': 0}
        
        for card, count in remaining_cards.items():
            value = card_values.get(card, 0)
            shoe.extend([value] * count)
            
        return shoe
    
    def _simulate_single_hand(self, shoe: List[int]) -> Dict:
        """Simula una sola mano de baccarat"""
        if len(shoe) < 6:  # Necesitamos al menos 6 cartas
            return {'winner': 'B', 'banker_score': 0, 'player_score': 0}
            
        # Repartir cartas iniciales
        banker_cards = [shoe.pop(0), shoe.pop(0)]
        player_cards = [shoe.pop(0), shoe.pop(0)]
        
        banker_score = self._calculate_baccarat_score(banker_cards)
        player_score = self._calculate_baccarat_score(player_cards)
        
        # Reglas de tercera carta
        if player_score <= 5:
            player_third = shoe.pop(0)
            player_cards.append(player_third)
            player_score = self._calculate_baccarat_score(player_cards)
            
            # Banker toma tercera carta según reglas
            if self._should_banker_draw(banker_score, player_third):
                banker_third = shoe.pop(0)
                banker_cards.append(banker_third)
                banker_score = self._calculate_baccarat_score(banker_cards)
        elif banker_score <= 5:
            banker_third = shoe.pop(0)
            banker_cards.append(banker_third)
            banker_score = self._calculate_baccarat_score(banker_cards)
            
        # Determinar ganador
        if banker_score > player_score:
            winner = 'B'
        elif player_score > banker_score:
            winner = 'P'
        else:
            winner = 'T'
            
        return {
            'winner': winner,
            'banker_score': banker_score,
            'player_score': player_score,
            'banker_cards': banker_cards,
            'player_cards': player_cards
        }
    
    def _calculate_baccarat_score(self, cards: List[int]) -> int:
        """Calcula puntuación baccarat"""
        total = sum(cards) % 10
        return total
    
    def _should_banker_draw(self, banker_score: int, player_third: int) -> bool:
        """Determina si el banquero debe tomar tercera carta"""
        if banker_score <= 2:
            return True
        elif banker_score == 3:
            return player_third != 8
        elif banker_score == 4:
            return player_third in [2, 3, 4, 5, 6, 7]
        elif banker_score == 5:
            return player_third in [4, 5, 6, 7]
        elif banker_score == 6:
            return player_third in [6, 7]
        else:
            return False
    
    def _get_card_value(self, card: str) -> str:
        """Obtiene valor de carta para conteo"""
        value_map = {
            'A': 'A', '2': '2', '3': '3', '4': '4', '5': '5', '6': '6', '7': '7', '8': '8', '9': '9',
            '10': '10', 'J': 'J', 'Q': 'Q', 'K': 'K'
        }
        return value_map.get(card, '10')
    
    def _analyze_simulation_results(self, results: List[Dict]) -> Dict:
        """Analiza resultados de las simulaciones"""
        total_hands = sum(len(sim['hands']) for sim in results)
        total_banker = sum(sim['total_banker_wins'] for sim in results)
        total_player = sum(sim['total_player_wins'] for sim in results)
        total_ties = sum(sim['total_ties'] for sim in results)
        
        if total_hands == 0:
            return self.base_probabilities.copy()
            
        # Calcular probabilidades ajustadas
        adjusted_probs = {
            'B': total_banker / total_hands,
            'P': total_player / total_hands,
            'T': total_ties / total_hands
        }
        
        # Aplicar suavizado bayesiano
        smoothing_factor = 0.1
        final_probs = {}
        for outcome in ['B', 'P', 'T']:
            final_probs[outcome] = (
                adjusted_probs[outcome] * (1 - smoothing_factor) + 
                self.base_probabilities[outcome] * smoothing_factor
            )
            
        # Normalizar
        total = sum(final_probs.values())
        final_probs = {k: v/total for k, v in final_probs.items()}
        
        return final_probs
    
    def _calculate_confidence_intervals(self, results: List[Dict]) -> Dict:
        """Calcula intervalos de confianza"""
        banker_probs = []
        player_probs = []
        tie_probs = []
        
        for sim in results:
            total = sim['total_banker_wins'] + sim['total_player_wins'] + sim['total_ties']
            if total > 0:
                banker_probs.append(sim['total_banker_wins'] / total)
                player_probs.append(sim['total_player_wins'] / total)
                tie_probs.append(sim['total_ties'] / total)
                
        return {
            'banker': {
                'mean': np.mean(banker_probs) if banker_probs else 0.4584,
                'std': np.std(banker_probs) if banker_probs else 0.05,
                'ci_95': 1.96 * (np.std(banker_probs) / np.sqrt(len(banker_probs))) if banker_probs else 0.05
            },
            'player': {
                'mean': np.mean(player_probs) if player_probs else 0.4461,
                'std': np.std(player_probs) if player_probs else 0.05,
                'ci_95': 1.96 * (np.std(player_probs) / np.sqrt(len(player_probs))) if player_probs else 0.05
            },
            'tie': {
                'mean': np.mean(tie_probs) if tie_probs else 0.0955,
                'std': np.std(tie_probs) if tie_probs else 0.02,
                'ci_95': 1.96 * (np.std(tie_probs) / np.sqrt(len(tie_probs))) if tie_probs else 0.02
            }
        }
    
    def _calculate_expected_value(self, probabilities: Dict) -> Dict:
        """Calcula valor esperado para cada tipo de apuesta"""
        # Pagos típicos: Banker 0.95:1, Player 1:1, Tie 8:1
        payouts = {'B': 0.95, 'P': 1.0, 'T': 8.0}
        
        expected_values = {}
        for outcome in ['B', 'P', 'T']:
            win_prob = probabilities[outcome]
            loss_prob = 1 - win_prob
            payout = payouts[outcome]
            
            # EV = (prob_ganar * ganancia) - (prob_perder * apuesta)
            ev = (win_prob * payout) - (loss_prob * 1)
            expected_values[outcome] = ev
            
        return expected_values


class BayesianUpdater:
    """Actualización bayesiana de probabilidades"""
    
    def __init__(self):
        self.prior_probabilities = {
            'B': 0.4584,
            'P': 0.4461,
            'T': 0.0955
        }
        
    def update_probabilities(self, evidence: Dict) -> Dict:
        """Actualiza probabilidades basado en evidencia"""
        likelihoods = self._calculate_likelihoods(evidence)
        
        # Aplicar teorema de Bayes
        posterior = {}
        evidence_prob = 0
        
        for outcome in ['B', 'P', 'T']:
            posterior[outcome] = likelihoods[outcome] * self.prior_probabilities[outcome]
            evidence_prob += posterior[outcome]
            
        # Normalizar
        for outcome in posterior:
            posterior[outcome] /= evidence_prob
            
        return posterior
    
    def _calculate_likelihoods(self, evidence: Dict) -> Dict:
        """Calcula verosimilitudes basado en evidencia"""
        # Evidencia puede incluir patrones, tendencias, etc.
        streak_length = evidence.get('streak_length', 0)
        chop_intensity = evidence.get('chop_intensity', 0)
        recent_pattern = evidence.get('recent_pattern', [])
        
        # Modelos de verosimilitud basados en patrones
        likelihoods = {'B': 1.0, 'P': 1.0, 'T': 1.0}
        
        # Ajustar por rachas
        if streak_length > 3:
            # Las rachas largas tienden a romperse
            current_streak = evidence.get('current_streak_type', 'B')
            if current_streak == 'B':
                likelihoods['P'] *= 1.1
                likelihoods['B'] *= 0.9
            else:
                likelihoods['B'] *= 1.1
                likelihoods['P'] *= 0.9
                
        # Ajustar por patrones de corte
        if chop_intensity > 0.7:
            # Alta intensidad de corte continúa
            likelihoods['B'] *= 1.05
            likelihoods['P'] *= 1.05
            likelihoods['T'] *= 0.9
            
        return likelihoods