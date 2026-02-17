import json
from pathlib import Path
from jsonschema import validate, ValidationError

def load_json_file(filename):
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"File {filename} not found")
        return None
    except json.JSONDecodeError:
        print(f"Could not decode JSON file {filename}.")
        return None
    
def validate_json_data(schema, data):
    try:
        validate(instance=data, schema=schema)
        print("Validation successful: The JSON data is valid.")
    except ValidationError as e:
        print("Validation failed")
        print(e.message)
    except Exception as e:
        print(f"Unexpected exception occurred: {e}")

if __name__ == "__main__":
    agent_response_schema = Path(__file__).parent/"schemas"/"agent_response.json"
    task_breakdown_schema = Path(__file__).parent/"schemas"/"task_breakdown.json"
    tool_call_schema = Path(__file__).parent/"schemas"/"tool_call.json"

    agent_response = Path(__file__).parent/"data"/"agent_response.json"
    task_breakdown = Path(__file__).parent/"data"/"task_breakdown.json"
    tool_call = Path(__file__).parent/"data"/"tool_call.json"

    agent_response_schema_data = load_json_file(agent_response_schema)
    task_breakdown_schema_data = load_json_file(task_breakdown_schema)
    tool_call_schema_data = load_json_file(tool_call_schema)

    agent_response_data = load_json_file(agent_response)
    task_breakdown_data = load_json_file(task_breakdown)
    tool_call_data = load_json_file(tool_call)

    schemas = [agent_response_schema_data, task_breakdown_schema_data, tool_call_schema_data]
    data = [agent_response_data, task_breakdown_data, tool_call_data]

    for i in range(len(schemas)):
        if schemas[i] and data[i]:
            validate_json_data(schemas[i], data[i])
