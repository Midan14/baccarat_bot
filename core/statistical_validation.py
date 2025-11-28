# core/statistical_validation.py
import numpy as np
from scipy import stats
from typing import List, Tuple, Dict

class StatisticalValidator:
    """Validador estadístico de aleatoriedad y sesgos"""
    
    @staticmethod
    def chi_square_uniformity(history: List[str]) -> Tuple[float, float, bool]:
        """
        Test Chi-cuadrado para uniformidad de resultados
        Returns: estadístico, p-value, es_aleatorio (p > 0.05)
        """
        if len(history) < 30:
            return 0.0, 1.0, False
        
        observed = [
            history.count('Dragon'),
            history.count('Tiger'),
            history.count('Tie')
        ]
        
        expected = [len(history) / 3] * 3  # Distribución uniforme esperada
        
        chi2, p_value = stats.chisquare(observed, expected)
        
        # Además, comparar con probabilidades teóricas del juego
        theoretical_expected = [
            len(history) * 0.446,  # Dragon
            len(history) * 0.446,  # Tiger
            len(history) * 0.108   # Tie
        ]
        
        chi2_theoretical, p_theoretical = stats.chisquare(observed, theoretical_expected)
        
        return chi2_theoretical, p_theoretical, p_theoretical > 0.05
    
    @staticmethod
    def runs_test(history: List[str]) -> Tuple[float, bool]:
        """
        Wald-Wolfowitz runs test para detectar patrones no aleatorios
        """
        if len(history) < 20:
            return 0.0, False
        
        # Convertir a secuencia binaria (considerar Tie como 2)
        sequence = np.array([0 if x == 'Dragon' else 1 if x == 'Tiger' else 2 for x in history])
        
        # Calcular runs (rachas)
        runs = 1
        for i in range(1, len(sequence)):
            if sequence[i] != sequence[i-1]:
                runs += 1
        
        # Estadístico de runs test
        n = len(sequence)
        n1 = np.sum(sequence == 0)
        n2 = np.sum(sequence == 1)
        
        expected_runs = (2 * n1 * n2 / n) + 1
        variance_runs = (expected_runs - 1) * (expected_runs - 2) / (n - 1)
        
        if variance_runs == 0:
            return 0.0, False
            
        z_stat = (runs - expected_runs) / np.sqrt(variance_runs)
        p_value = 2 * (1 - stats.norm.cdf(abs(z_stat)))
        
        return p_value, p_value > 0.05  # True si es aleatorio
    
    @staticmethod
    def markov_chain_analysis(history: List[str]) -> Dict[str, np.ndarray]:
        """
        Análisis de cadenas de Markov para transiciones de estado
        Returns: matriz de transición 3x3 (Dragon, Tiger, Tie)
        """
        if len(history) < 50:
            return {}
        
        states = {'Dragon': 0, 'Tiger': 1, 'Tie': 2}
        matrix = np.zeros((3, 3))
        
        for i in range(len(history) - 1):
            current = states.get(history[i], -1)
            next_state = states.get(history[i+1], -1)
            
            if current >= 0 and next_state >= 0:
                matrix[current, next_state] += 1
        
        # Normalizar por filas (probabilidades condicionales)
        row_sums = matrix.sum(axis=1, keepdims=True)
        row_sums[row_sums == 0] = 1  # Evitar división por cero
        
        transition_matrix = matrix / row_sums
        
        return {
            'transition_matrix': transition_matrix,
            'stationary_distribution': StatisticalValidator._stationary_distribution(transition_matrix),
            'is_ergodic': StatisticalValidator._is_ergodic(transition_matrix)
        }
    
    @staticmethod
    def _stationary_distribution(matrix: np.ndarray) -> np.ndarray:
        """Calcular distribución estacionaria de la cadena de Markov"""
        eigenvals, eigenvecs = np.linalg.eig(matrix.T)
        stationary = np.array(eigenvecs[:, np.isclose(eigenvals, 1)])
        stationary = stationary / stationary.sum()
        return stationary.real
    
    @staticmethod
    def _is_ergodic(matrix: np.ndarray) -> bool:
        """Verificar si la cadena es ergódica (puede alcanzar cualquier estado)"""
        # Comprobar si la matriz es irreducible y aperiódica
        return np.all(np.linalg.matrix_power(matrix, 10) > 0)
    
    @staticmethod
    def volatility_analysis(history: List[str], window: int = 20) -> Dict[str, float]:
        """
        Análisis de volatilidad para ajustar tamaño de apuesta
        """
        if len(history) < window:
            return {'volatility': 0.0, 'sharpe_ratio': 0.0}
        
        # Calcular retornos (1 = win, -1 = loss, 0 = tie)
        returns = []
        for i in range(1, len(history)):
            if history[i] != history[i-1]:
                returns.append(-1)  # Cambio = pérdida (si apostamos igual)
            elif history[i] == 'Dragon':
                returns.append(1 if history[i-1] == 'Dragon' else -1)
            # Mejorar esto con datos reales de apuestas
        
        returns = np.array(returns[-window:])
        
        volatility = np.std(returns)
        mean_return = np.mean(returns)
        
        sharpe = mean_return / volatility if volatility > 0 else 0
        
        return {
            'volatility': volatility,
            'sharpe_ratio': sharpe,
            'recommended_bet_multiplier': min(2.0, max(0.5, 1 / (1 + volatility)))
        }

# Uso en el motor de decisión
def should_trust_prediction(history: List[str], prediction: str, confidence: float) -> Tuple[bool, str]:
    """
    Decidir si confiar en una predicción basado en validación estadística
    """
    validator = StatisticalValidator()
    
    # Test 1: ¿Es el juego realmente predecible?
    chi2, p_chi2, is_uniform = validator.chi_square_uniformity(history)
    _, p_runs, is_random = validator.runs_test(history)
    
    if is_random and p_chi2 > 0.1:
        return False, "Juego demasiado aleatorio - NO apostar"
    
    # Test 2: Análisis de volatilidad
    vol_data = validator.volatility_analysis(history)
    if vol_data['volatility'] > 0.8:
        return False, "Alta volatilidad - Reducir exposición"
    
    # Test 3: Validar confianza vs volatilidad
    if confidence < vol_data['recommended_bet_multiplier'] * 0.5:
        return False, "Confianza insuficiente para volatilidad actual"
    
    return True, "Predicción validada estadísticamente"