import pytest
from ml.anomaly_detector import AnomalyDetector

def test_anomaly_detector():
    detector = AnomalyDetector()
    
    # Test loading results
    results = detector.load_test_results()
    assert len(results) > 0
    
    # Test feature extraction
    features = detector.extract_features(results)
    assert features.shape[1] == 5  # 5 features per test case
    
    # Test response time anomaly detection
    time_anomalies = detector.detect_response_time_anomalies(results)
    assert isinstance(time_anomalies, list)
    
    # Test status code anomaly detection
    status_anomalies = detector.detect_status_code_anomalies(results)
    assert isinstance(status_anomalies, list)
    
    # Test pattern anomaly detection
    pattern_anomalies = detector.detect_pattern_anomalies(results)
    assert isinstance(pattern_anomalies, list)

def test_anomaly_analysis():
    detector = AnomalyDetector()
    analysis = detector.analyze()
    
    # Verify analysis structure
    assert 'total_tests' in analysis
    assert 'anomalies' in analysis
    assert 'summary' in analysis
    assert 'analyzed_at' in analysis
    
    # Verify anomaly categories
    assert 'response_time' in analysis['anomalies']
    assert 'status_code' in analysis['anomalies']
    assert 'pattern' in analysis['anomalies']
    
    # Verify summary statistics
    assert analysis['summary']['total_anomalies'] == (
        analysis['summary']['response_time_anomalies'] +
        analysis['summary']['status_code_anomalies'] +
        analysis['summary']['pattern_anomalies']
    )