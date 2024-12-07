import pytest
from specs.api_parser import APIParser  # Changed to absolute import

def test_api_parser():
    swagger_url = "https://fakerestapi.azurewebsites.net/swagger/v1/swagger.json"
    parser = APIParser(swagger_url)
    parser.parse_specification()
    
    assert len(parser.endpoints) > 0
    
    # Verify endpoint structure
    first_endpoint = parser.endpoints[0]
    assert first_endpoint.path
    assert first_endpoint.method in ['GET', 'POST', 'PUT', 'DELETE']
    assert isinstance(first_endpoint.parameters, list)
    assert isinstance(first_endpoint.responses, dict)