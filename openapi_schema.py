import requests
from pydantic import BaseModel, create_model, Field


# Map OpenAPI types to Python/Pydantic types
OPENAPI_TO_PYTHON_TYPES = {
    "string": str,
    "integer": int,
    "number": float,
    "boolean": bool,
    "array": list,
    "object": dict,
}


# Fetch OpenAPI Schema
def get_openapi_schema(host: str = "localhost", port: int = 8080) -> dict[str, dict]:
    schema_url = f"http://{host}:{port}/openapi.json"
    openapi_schema = requests.get(schema_url).json()
    return openapi_schema


# Dynamically generate models from OpenAPI schema definitions
def get_models(openapi_schema: dict) -> dict[str, BaseModel]:
    models = {}
    for name, schema in openapi_schema.get("components", {}).get("schemas", {}).items():
        fields = {}
        for field_name, field_props in schema.get("properties", {}).items():
            field_type = OPENAPI_TO_PYTHON_TYPES.get(
                field_props.get("type"), str
            )  # Default to str
            field_constraints = {}

            # Add constraints (e.g., minimum, maximum, etc.)
            if "minimum" in field_props:
                field_constraints["ge"] = field_props["minimum"]
            if "maximum" in field_props:
                field_constraints["le"] = field_props["maximum"]

            # Use Field to include constraints
            fields[field_name] = (field_type, Field(**field_constraints))

        # Create model dynamically
        models[name] = create_model(name, **fields)
    return models


def get_model_for_endpoint(endpoint: str, openapi_schema: dict) -> BaseModel:
    models = get_models(openapi_schema)
    print("✅ Models:", models)

    # Extract schema reference from OpenAPI paths
    request_body = (
        openapi_schema["paths"].get(endpoint, {}).get("get", {}).get("requestBody", {})
    )
    schema_ref = (
        request_body.get("content", {})
        .get("application/json", {})
        .get("schema", {})
        .get("$ref", "")
    )

    if not schema_ref:
        raise ValueError(f"No schema reference found for endpoint: {endpoint}")

    # Extract the schema name from the reference
    schema_name = schema_ref.split("/")[-1]
    RequestModel = models.get(schema_name)

    if not RequestModel:
        raise ValueError(f"Schema '{schema_name}' not found in models.")
    return RequestModel


def validate_arguments(schema: dict, endpoint: str, arguments: dict) -> BaseModel:
    RequestModel = get_model_for_endpoint(endpoint, schema)
    return RequestModel(**arguments)


host = "localhost"
port = 8080
endpoint = "/users"
payload = {"name": "Alice", "age": 1}
print("✅ With payload:", payload)

openapi_schema = get_openapi_schema(host, port)
try:
    model = validate_arguments(openapi_schema, endpoint, payload)
    print("✅ Request is valid!")
except Exception as e:
    print(f"❌ Error: {e}")

response = requests.get(
    f"http://localhost:8080{endpoint}", json=model.model_dump()
).json()
print("✅ Response:", response)
