from typing import Dict, List
import requests
from pydantic import BaseModel, Field
import json

class EndpointSpec(BaseModel):
    path: str
    method: str
    parameters: List[Dict] = Field(default_factory=list)
    responses: Dict = Field(default_factory=dict)
    description: str = ""

class APIParser:
    def __init__(self, swagger_url: str):
        self.swagger_url = swagger_url
        self.endpoints: List[EndpointSpec] = []

    def fetch_swagger_spec(self) -> Dict:
        """Fetch Swagger/OpenAPI specification from the URL"""
        response = requests.get(self.swagger_url)
        response.raise_for_status()
        return response.json()

    def parse_parameters(self, path_item: Dict, method_spec: Dict) -> List[Dict]:
        """Extract parameters from path and method specifications"""
        parameters = []
        # Path parameters
        parameters.extend(path_item.get('parameters', []))
        # Method parameters
        parameters.extend(method_spec.get('parameters', []))
        return parameters

    def parse_specification(self):
        """Parse the OpenAPI specification and extract endpoint details"""
        spec = self.fetch_swagger_spec()
        
        for path, path_item in spec['paths'].items():
            for method, method_spec in path_item.items():
                if method in ['get', 'post', 'put', 'delete']:
                    endpoint = EndpointSpec(
                        path=path,
                        method=method.upper(),
                        parameters=self.parse_parameters(path_item, method_spec),
                        responses=method_spec.get('responses', {}),
                        description=method_spec.get('description', '')
                    )
                    self.endpoints.append(endpoint)

    def export_endpoints(self, output_file: str = 'specs/endpoints.json'):
        """Export parsed endpoints to a JSON file"""
        with open(output_file, 'w') as f:
            json.dump(
                [endpoint.model_dump() for endpoint in self.endpoints],
                f,
                indent=2
            )

def main():
    swagger_url = "https://fakerestapi.azurewebsites.net/swagger/v1/swagger.json"
    parser = APIParser(swagger_url)
    parser.parse_specification()
    parser.export_endpoints()

if __name__ == "__main__":
    main()