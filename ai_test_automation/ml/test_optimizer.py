from typing import List, Dict, Any
import json
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from pathlib import Path

class TestOptimizer:
    def __init__(self, results_file: str = 'test_results/execution_results.json'):
        self.results_file = results_file
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        
    def load_execution_history(self) -> List[Dict]:
        """Load test execution history"""
        with open(self.results_file, 'r') as f:
            return json.load(f)

    def extract_features(self, test_results: List[Dict]) -> np.ndarray:
        """Extract features from test execution history"""
        features = []
        for result in test_results:
            feature_vector = [
                float(result['response_time']),
                1 if result['passed'] else 0,
                1 if result['method'] == 'GET' else 2 if result['method'] == 'POST' else 3 if result['method'] == 'PUT' else 4,
                len(result['parameters']),
                1 if 'response_data' in result else 0
            ]
            features.append(feature_vector)
        return np.array(features)

    def extract_labels(self, test_results: List[Dict]) -> np.ndarray:
        """Extract labels (priority) based on historical failures and response times"""
        labels = []
        for result in test_results:
            # High priority if test failed or had high response time
            priority = 2 if not result['passed'] else \
                      1 if result['response_time'] > 1.0 else 0
            labels.append(priority)
        return np.array(labels)

    def train_model(self):
        """Train the ML model on historical test data"""
        history = self.load_execution_history()
        
        # Extract features and labels
        X = self.extract_features(history)
        y = self.extract_labels(history)
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Train model
        self.model.fit(X_scaled, y)

    def predict_priority(self, test_case: Dict) -> int:
        """Predict priority for a new test case"""
        # Create feature vector for the test case
        feature_vector = np.array([[
            0.0,  # Default response time
            1.0,  # Assume pass
            1 if test_case['method'] == 'GET' else 2 if test_case['method'] == 'POST' else 3 if test_case['method'] == 'PUT' else 4,
            len(test_case['parameters']),
            0  # Default no response data
        ]])
        
        # Scale features
        feature_vector_scaled = self.scaler.transform(feature_vector)
        
        # Predict priority
        return self.model.predict(feature_vector_scaled)[0]

    def optimize_test_suite(self, test_cases: List[Dict]) -> List[Dict]:
        """Optimize test suite by prioritizing test cases"""
        # Train model on historical data
        self.train_model()
        
        # Predict priorities for all test cases
        for test_case in test_cases:
            test_case['priority'] = int(self.predict_priority(test_case))
        
        # Sort test cases by priority (2=High, 1=Medium, 0=Low)
        optimized_cases = sorted(test_cases, key=lambda x: x['priority'], reverse=True)
        
        return optimized_cases

    def export_optimized_suite(self, test_cases: List[Dict], output_file: str = 'test_cases/optimized_tests.json'):
        """Export optimized test suite to JSON file"""
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w') as f:
            json.dump(test_cases, f, indent=2)

def main():
    # Load original test cases
    with open('test_cases/generated_tests.json', 'r') as f:
        test_cases = json.load(f)
    
    # Create and run optimizer
    optimizer = TestOptimizer()
    optimized_cases = optimizer.optimize_test_suite(test_cases)
    optimizer.export_optimized_suite(optimized_cases)

if __name__ == "__main__":
    main()