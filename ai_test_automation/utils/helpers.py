from typing import Dict, List, Any
import json
from pathlib import Path

def validate_response_schema(response_data: Any, expected_schema: Dict) -> bool:
    """Validate response data against expected schema"""
    if not expected_schema:
        return True
        
    schema_type = expected_schema.get('type', 'object')
    
    if schema_type == 'array':
        return (
            isinstance(response_data, list) and
            all(isinstance(item, dict) for item in response_data)
        )
    elif schema_type == 'object':
        return isinstance(response_data, dict)
    
    return True

def generate_test_report(results: List[Dict], output_file: str = 'test_results/test_report.md'):
    """Generate a markdown report from test results"""
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)
    
    total_tests = len(results)
    passed_tests = sum(1 for r in results if r['passed'])
    failed_tests = total_tests - passed_tests
    
    report = [
        "# API Test Execution Report\n",
        f"- Total Tests: {total_tests}",
        f"- Passed: {passed_tests}",
        f"- Failed: {failed_tests}",
        f"- Success Rate: {(passed_tests/total_tests)*100:.2f}%\n",
        "## Failed Tests\n"
    ]
    
    # Add failed test details
    for result in results:
        if not result['passed']:
            report.extend([
                f"### {result['test_case']}",
                f"- Endpoint: {result['endpoint']}",
                f"- Method: {result['method']}",
                f"- Parameters: {json.dumps(result['parameters'], indent=2)}",
                f"- Expected Status: {result['expected_status']}",
                f"- Actual Status: {result.get('actual_status', 'N/A')}",
                f"- Error: {result.get('error', 'N/A')}\n"
            ])
    
    with open(output_file, 'w') as f:
        f.write('\n'.join(report))
