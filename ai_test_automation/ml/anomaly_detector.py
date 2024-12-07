from typing import List, Dict, Any
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest
from sklearn.cluster import DBSCAN
import json
from datetime import datetime
from pathlib import Path

class AnomalyDetector:
    def __init__(self, results_file: str = 'test_results/execution_results.json'):
        self.results_file = results_file
        self.scaler = StandardScaler()
        self.isolation_forest = IsolationForest(
            contamination=0.1,  # Expected proportion of anomalies
            random_state=42
        )
        self.dbscan = DBSCAN(
            eps=0.5,  # Maximum distance between samples
            min_samples=5  # Minimum samples in a cluster
        )

    def load_test_results(self) -> List[Dict]:
        """Load test execution results"""
        with open(self.results_file, 'r') as f:
            return json.load(f)

    def extract_features(self, results: List[Dict]) -> np.ndarray:
        """Extract features for anomaly detection"""
        features = []
        for result in results:
            feature_vector = [
                float(result['response_time']),
                int(result['actual_status']),
                1 if result['passed'] else 0,
                len(result.get('response_data', {})) if isinstance(result.get('response_data'), dict) else 0,
                1 if 'error' in result else 0
            ]
            features.append(feature_vector)
        return np.array(features)

    def detect_response_time_anomalies(self, results: List[Dict]) -> List[Dict]:
        """Detect anomalies in response times using Isolation Forest"""
        response_times = np.array([r['response_time'] for r in results]).reshape(-1, 1)
        scaled_times = self.scaler.fit_transform(response_times)
        
        # Predict anomalies (-1 for anomalies, 1 for normal)
        predictions = self.isolation_forest.fit_predict(scaled_times)
        
        anomalies = []
        for idx, (pred, result) in enumerate(zip(predictions, results)):
            if pred == -1:  # Anomaly detected
                anomalies.append({
                    'type': 'response_time',
                    'endpoint': result['endpoint'],
                    'method': result['method'],
                    'response_time': result['response_time'],
                    'average_time': float(np.mean(response_times)),
                    'std_dev': float(np.std(response_times)),
                    'z_score': float((result['response_time'] - np.mean(response_times)) / np.std(response_times)),
                    'timestamp': result['executed_at']
                })
        return anomalies

    def detect_status_code_anomalies(self, results: List[Dict]) -> List[Dict]:
        """Detect anomalies in status codes using clustering"""
        features = np.array([(r['actual_status'], r['response_time']) for r in results])
        scaled_features = self.scaler.fit_transform(features)
        
        # Cluster similar responses
        clusters = self.dbscan.fit_predict(scaled_features)
        
        anomalies = []
        for idx, (cluster, result) in enumerate(zip(clusters, results)):
            if cluster == -1:  # Noise points are considered anomalies
                anomalies.append({
                    'type': 'status_code',
                    'endpoint': result['endpoint'],
                    'method': result['method'],
                    'status_code': result['actual_status'],
                    'expected_status': result['expected_status'],
                    'response_time': result['response_time'],
                    'timestamp': result['executed_at']
                })
        return anomalies

    def detect_pattern_anomalies(self, results: List[Dict]) -> List[Dict]:
        """Detect anomalies in response patterns"""
        features = self.extract_features(results)
        scaled_features = self.scaler.fit_transform(features)
        
        # Use Isolation Forest for pattern detection
        predictions = self.isolation_forest.fit_predict(scaled_features)
        
        anomalies = []
        for idx, (pred, result) in enumerate(zip(predictions, results)):
            if pred == -1:
                anomalies.append({
                    'type': 'pattern',
                    'endpoint': result['endpoint'],
                    'method': result['method'],
                    'status_code': result['actual_status'],
                    'response_time': result['response_time'],
                    'passed': result['passed'],
                    'timestamp': result['executed_at']
                })
        return anomalies

    def analyze(self) -> Dict[str, Any]:
        """Perform comprehensive anomaly analysis"""
        results = self.load_test_results()
        
        # Detect different types of anomalies
        response_time_anomalies = self.detect_response_time_anomalies(results)
        status_code_anomalies = self.detect_status_code_anomalies(results)
        pattern_anomalies = self.detect_pattern_anomalies(results)
        
        # Aggregate analysis results
        analysis = {
            'total_tests': len(results),
            'anomalies': {
                'response_time': response_time_anomalies,
                'status_code': status_code_anomalies,
                'pattern': pattern_anomalies
            },
            'summary': {
                'total_anomalies': len(response_time_anomalies) + len(status_code_anomalies) + len(pattern_anomalies),
                'response_time_anomalies': len(response_time_anomalies),
                'status_code_anomalies': len(status_code_anomalies),
                'pattern_anomalies': len(pattern_anomalies)
            },
            'analyzed_at': datetime.now().isoformat()
        }
        
        return analysis

    def export_analysis(self, analysis: Dict[str, Any], output_file: str = 'test_results/anomaly_analysis.json'):
        """Export anomaly analysis results"""
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w') as f:
            json.dump(analysis, f, indent=2)

def main():
    detector = AnomalyDetector()
    analysis = detector.analyze()
    detector.export_analysis(analysis)
    
    # Print summary
    print("\nAnomaly Detection Summary:")
    print(f"Total Tests Analyzed: {analysis['total_tests']}")
    print(f"Total Anomalies Found: {analysis['summary']['total_anomalies']}")
    print(f"- Response Time Anomalies: {analysis['summary']['response_time_anomalies']}")
    print(f"- Status Code Anomalies: {analysis['summary']['status_code_anomalies']}")
    print(f"- Pattern Anomalies: {analysis['summary']['pattern_anomalies']}")

if __name__ == "__main__":
    main()