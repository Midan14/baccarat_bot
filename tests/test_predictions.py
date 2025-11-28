# tests/test_predictions.py
import pytest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from core.prediction_engine import PredictionEngine

class TestPredictionEngine:
    
    def setup_method(self):
        self.engine = PredictionEngine()
    
    def test_trend_analysis_anti_trend(self):
        """Test análisis de tendencia (estrategia anti-tendencia)"""
        history = ['B', 'B', 'B', 'B']  # 4 Bankers seguidos
        result = self.engine._trend_analysis(history)
        
        assert result.signal == 'P'
        assert result.confidence > 0
        assert result.algorithm == 'TREND'
    
    def test_frequency_analysis_balance(self):
        """Test análisis de frecuencia (estrategia de balance)"""
        history = ['B', 'B', 'B', 'P', 'P']  # Más Bankers que Players
        result = self.engine._frequency_analysis(history)
        
        assert result.signal == 'P'  # Debería apostar por Player (atrasado)
        assert result.confidence > 0
        assert result.algorithm == 'FREQUENCY'
    
    def test_insufficient_data(self):
        """Test con datos insuficientes"""
        history = ['B', 'P']
        result = self.engine.analyze(history)
        
        assert result.signal == 'NONE'
        assert result.confidence == 0.0
    
    def test_pattern_recognition_alternating(self):
        """Test reconocimiento de patrón alternante"""
        history = ['B', 'P', 'B', 'P', 'B']  # Patrón alternante
        result = self.engine._pattern_recognition(history[-4:])
        
        # Debería detectar el patrón y predecir continuación
        assert result.signal == 'B'
        assert result.algorithm == 'PATTERN'

if __name__ == "__main__":
    pytest.main([__file__, "-v"])