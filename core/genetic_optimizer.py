# core/genetic_optimizer.py
import numpy as np
from typing import List, Dict, Callable
from dataclasses import dataclass
import random

@dataclass
class Individual:
    """Individuo en el algoritmo genético"""
    genes: Dict[str, float]  # Parámetros a optimizar
    fitness: float = 0.0

class GeneticParameterOptimizer:
    """Optimizar parámetros del bot usando algoritmos genéticos"""
    
    def __init__(self, history: List[str], evaluation_func: Callable):
        self.history = history
        self.evaluate = evaluation_func
        self.population_size = 20
        self.generations = 15
        self.mutation_rate = 0.1
        
    def optimize(self) -> Dict[str, float]:
        """Ejecutar optimización genética"""
        
        # 1. Inicializar población
        population = self._initialize_population()
        
        # 2. Evolucionar
        for generation in range(self.generations):
            # Evaluar fitness
            for individual in population:
                if individual.fitness == 0:
                    individual.fitness = self.evaluate(individual.genes, self.history)
            
            # Seleccionar mejores
            population = self._select_population(population)
            
            # Cruzamiento
            offspring = self._crossover(population)
            
            # Mutación
            offspring = self._mutate(offspring)
            
            # Reemplazar
            population.extend(offspring)
        
        # Devolver mejor individuo
        best = max(population, key=lambda x: x.fitness)
        return best.genes
    
    def _initialize_population(self) -> List[Individual]:
        """Crear población inicial aleatoria"""
        population = []
        for _ in range(self.population_size):
            genes = {
                'confidence_threshold': random.uniform(0.3, 0.6),
                'min_history_length': random.randint(30, 80),
                'trend_weight': random.uniform(0.1, 0.4),
                'frequency_weight': random.uniform(0.1, 0.4),
                'pattern_weight': random.uniform(0.1, 0.4),
                'lightning_weight': random.uniform(0.1, 0.4),
                'kelly_fraction': random.uniform(0.1, 0.4)
            }
            population.append(Individual(genes))
        
        return population
    
    def _select_population(self, population: List[Individual]) -> List[Individual]:
        """Selección por torneo"""
        selected = []
        for _ in range(self.population_size):
            # Torneo de 3
            fighters = random.sample(population, 3)
            winner = max(fighters, key=lambda x: x.fitness)
            selected.append(Individual(winner.genes.copy(), winner.fitness))
        
        return selected
    
    def _crossover(self, parents: List[Individual]) -> List[Individual]:
        """Cruzamiento de un punto"""
        offspring = []
        for i in range(0, len(parents), 2):
            if i + 1 >= len(parents):
                break
            
            parent1, parent2 = parents[i], parents[i+1]
            
            # Crear hijos
            child1_genes = {}
            child2_genes = {}
            
            for key in parent1.genes:
                if random.random() < 0.5:
                    child1_genes[key] = parent1.genes[key]
                    child2_genes[key] = parent2.genes[key]
                else:
                    child1_genes[key] = parent2.genes[key]
                    child2_genes[key] = parent1.genes[key]
            
            offspring.extend([
                Individual(child1_genes),
                Individual(child2_genes)
            ])
        
        return offspring
    
    def _mutate(self, population: List[Individual]) ->