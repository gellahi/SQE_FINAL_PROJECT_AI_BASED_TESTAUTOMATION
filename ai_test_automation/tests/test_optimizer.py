import pytest
import json  # Add this import
from ml.test_optimizer import TestOptimizer

def test_test_optimizer():
    optimizer = TestOptimizer()
    
    # Test loading execution history
    history = optimizer.load_execution_history()
    assert len(history) > 0
    
    # Test feature extraction
    features = optimizer.extract_features(history)
    assert features.shape[1] == 5  # 5 features per test case
    
    # Test model training
    optimizer.train_model()
    
    # Test priority prediction
    test_case = {
        'method': 'GET',
        'parameters': {},
        'endpoint': '/api/test'
    }
    priority = optimizer.predict_priority(test_case)
    assert priority in [0, 1, 2]  # Low, Medium, High

def test_suite_optimization():
    optimizer = TestOptimizer()
    
    # Load test cases
    with open('test_cases/generated_tests.json', 'r') as f:
        test_cases = json.load(f)
    
    # Optimize test suite
    optimized = optimizer.optimize_test_suite(test_cases)
    
    assert len(optimized) == len(test_cases)
    assert all('priority' in tc for tc in optimized)
    
    # Verify priority ordering
    priorities = [tc['priority'] for tc in optimized]
    assert priorities == sorted(priorities, reverse=True)