import pytest
import json
import requests
from typing import Dict, List
from pathlib import Path
from datetime import datetime
from test_cases.generate_tests import TestCase

class TestExecutor:
    def __init__(self, base_url: str = "https://fakerestapi.azurewebsites.net"):
        self.base_url = base_url
        self.test_cases = self._load_test_cases()
        self.results: List[Dict] = []

    def _load_test_cases(self) -> List[TestCase]:
        """Load generated test cases from JSON file"""
        with open('test_cases/generated_tests.json', 'r') as f:
            test_data = json.load(f)
            return [
                TestCase(
                    endpoint=tc['endpoint'],
                    method=tc['method'],
                    parameters=tc['parameters'],
                    expected_status=tc['expected_status'],
                    description=tc['description']
                )
                for tc in test_data
            ]

    def execute_test(self, test_case: TestCase) -> Dict:
        """Execute a single test case"""
        url = f"{self.base_url}{test_case.endpoint}"
        
        # Replace path parameters in URL
        for param_name, param_value in test_case.parameters.items():
            if f"{{{param_name}}}" in url:
                url = url.replace(f"{{{param_name}}}", str(param_value))
        
        try:
            response = requests.request(
                method=test_case.method,
                url=url,
                json=test_case.parameters if test_case.method in ['POST', 'PUT'] else None,
                params={k:v for k,v in test_case.parameters.items() if f"{{{k}}}" not in test_case.endpoint}
            )
            
            result = {
                'test_case': test_case.description,
                'endpoint': test_case.endpoint,
                'method': test_case.method,
                'parameters': test_case.parameters,
                'expected_status': test_case.expected_status,
                'actual_status': response.status_code,
                'response_time': response.elapsed.total_seconds(),
                'passed': response.status_code == test_case.expected_status,
                'response_data': response.json() if response.text else None,
                'executed_at': datetime.now().isoformat()
            }
            
            self.results.append(result)
            return result
            
        except requests.RequestException as e:
            result = {
                'test_case': test_case.description,
                'endpoint': test_case.endpoint,
                'method': test_case.method,
                'parameters': test_case.parameters,
                'expected_status': test_case.expected_status,
                'error': str(e),
                'passed': False,
                'executed_at': datetime.now().isoformat()
            }
            self.results.append(result)
            return result

    def export_results(self, output_file: str = 'test_results/execution_results.json'):
        """Export test execution results to JSON file"""
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w') as f:
            json.dump(self.results, f, indent=2)

def load_test_cases() -> List[TestCase]:
    """Load test cases for pytest parametrize"""
    executor = TestExecutor()
    return executor.test_cases

# Pytest test cases
@pytest.mark.parametrize("test_case", load_test_cases())
def test_api_endpoints(test_case: TestCase):
    """Execute API test cases"""
    executor = TestExecutor()
    result = executor.execute_test(test_case)
    
    # Custom error message for assertion
    error_msg = (
        f"\nTest: {result['test_case']}"
        f"\nEndpoint: {result['endpoint']}"
        f"\nMethod: {result['method']}"
        f"\nParameters: {result['parameters']}"
        f"\nExpected Status: {result['expected_status']}"
        f"\nActual Status: {result.get('actual_status', 'N/A')}"
        f"\nError: {result.get('error', 'N/A')}"
    )
    
    assert result['passed'], error_msg
    
    # Additional assertions for response data
    # Update the response data check
    if 'response_data' in result:
        if result['method'] != 'DELETE':  # Only check JSON for non-DELETE methods
            assert isinstance(result['response_data'], (dict, list)), "Response data should be JSON"
        assert result['response_time'] < 5.0, "Response time should be less than 5 seconds"

def test_execution_summary():
    """Generate and verify test execution summary"""
    executor = TestExecutor()
    
    # Execute all test cases
    for test_case in executor.test_cases:
        executor.execute_test(test_case)
    
    # Export results
    executor.export_results()
    
    # Verify test execution stats
    total_tests = len(executor.results)
    passed_tests = sum(1 for r in executor.results if r['passed'])
    failed_tests = total_tests - passed_tests
    
    print(f"\nTest Execution Summary:")
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {failed_tests}")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.2f}%")
    
    assert total_tests > 0, "No tests were executed"
    assert passed_tests > 0, "No tests passed"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])