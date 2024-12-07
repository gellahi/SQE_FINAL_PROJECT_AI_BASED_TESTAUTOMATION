from typing import List, Dict, Any
import json
import random
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime

@dataclass
class TestCase:
    endpoint: str
    method: str
    parameters: Dict[str, Any]
    expected_status: int
    description: str

class TestGenerator:
    def __init__(self, endpoints_file: str = 'specs/endpoints.json'):
        self.endpoints = self._load_endpoints(endpoints_file)
        self.test_cases: List[TestCase] = []

    def _load_endpoints(self, file_path: str) -> List[Dict]:
        """Load endpoints from the JSON file"""
        with open(file_path, 'r') as f:
            return json.load(f)

    def generate_parameter_value(self, param_spec: Dict) -> Any:
        """Generate test values based on parameter specifications"""
        schema = param_spec.get('schema', {})
        param_type = schema.get('type')
        param_name = param_spec.get('name', '')
        
        if param_type == 'integer':
            if param_name.lower() in ['id', 'idbook']:  # Special handling for IDs
                return random.choice([
                    1,      # Valid minimum ID
                    50,     # Valid middle ID 
                    99,     # Valid maximum ID
                ])
            else:
                return random.choice([
                    1,      # Valid minimum
                    100,    # Valid middle
                    999,    # Valid maximum
                    -1,     # Invalid negative
                    0,      # Edge case
                ])
        elif param_type == 'string':
            return random.choice([
                'test_string',
                '',  # Empty string
                'A' * 256,  # Long string
                'Special@#$%Characters',
            ])
        return None

    def generate_test_cases(self) -> List[TestCase]:
        """Generate test cases for all endpoints"""
        for endpoint in self.endpoints:
            path = endpoint['path']
            method = endpoint['method']
            parameters = endpoint['parameters']

            # Generate positive test case
            param_values = {}
            for param in parameters:
                param_values[param['name']] = self.generate_parameter_value(param)
            
            self.test_cases.append(
                TestCase(
                    endpoint=path,
                    method=method,
                    parameters=param_values,
                    expected_status=200,  # Default success status
                    description=f"Valid {method} request to {path}"
                )
            )

            # Generate negative test cases
            if parameters:
                # Missing required parameter
                for param in parameters:
                    if param.get('required', False):
                        invalid_params = param_values.copy()
                        invalid_params[param['name']] = None
                        self.test_cases.append(
                            TestCase(
                                endpoint=path,
                                method=method,
                                parameters=invalid_params,
                                expected_status=400,
                                description=f"Missing required parameter {param['name']}"
                            )
                        )

        return self.test_cases

    def export_test_cases(self, output_file: str = 'test_cases/generated_tests.json'):
        """Export generated test cases to JSON file"""
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w') as f:
            json.dump(
                [
                    {
                        'endpoint': tc.endpoint,
                        'method': tc.method,
                        'parameters': tc.parameters,
                        'expected_status': tc.expected_status,
                        'description': tc.description,
                        'generated_at': datetime.now().isoformat()
                    }
                    for tc in self.test_cases
                ],
                f,
                indent=2
            )

def main():
    generator = TestGenerator()
    generator.generate_test_cases()
    generator.export_test_cases()

if __name__ == "__main__":
    main()