import pytest
from test_cases.generate_tests import TestGenerator, TestCase

def test_test_generator():
    generator = TestGenerator()
    test_cases = generator.generate_test_cases()
    
    assert len(test_cases) > 0
    
    # Verify test case structure
    first_case = test_cases[0]
    assert isinstance(first_case, TestCase)
    assert first_case.endpoint.startswith('/api/v1/')
    assert first_case.method in ['GET', 'POST', 'PUT', 'DELETE']
    assert isinstance(first_case.parameters, dict)
    assert isinstance(first_case.expected_status, int)
    assert isinstance(first_case.description, str)

def test_parameter_generation():
    generator = TestGenerator()
    
    # Test integer parameter generation
    int_param = {
        'schema': {
            'type': 'integer',
            'format': 'int32'
        }
    }
    int_value = generator.generate_parameter_value(int_param)
    assert isinstance(int_value, int)
    
    # Test string parameter generation
    str_param = {
        'schema': {
            'type': 'string'
        }
    }
    str_value = generator.generate_parameter_value(str_param)
    assert isinstance(str_value, (str, type(None)))