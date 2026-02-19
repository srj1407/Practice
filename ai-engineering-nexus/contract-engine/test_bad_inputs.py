import os
import uuid
import json

from pydantic import ValidationError
from models import TaskBreakdown, ToolCall
import asyncio

right_response = {
    "tools": [
        {
            "tool_name": "add",
            "parameters": {"a": 5, "b": 2},
            "reasoning": "Addition"
        }
    ]
}

bad_response_1 = {
    "tools": [
        {
            "tool_name": "sub",
            "parameters": {"a": 5, "b": 2},
            "reasoning": "Subtraction"
        }
    ]
}

bad_response_2 = {
    "tools": [
        {
            "tool_name": "subtract",
            "reasoning": "Subtraction"
        }
    ]
}

# Test 3: Invalid confidence
bad_response_3 = {
    "tool_name": "calculator",
    "parameters": {"a": 5},
    "confidence": 999
}

try:
    result = ToolCall.model_validate(bad_response_1)
except ValidationError as e:
    print(str(e))

try:
    result = ToolCall.model_validate(bad_response_2)
except ValidationError as e:
    print(str(e))

try:
    result = ToolCall.model_validate(bad_response_3)
except ValidationError as e:
    print(str(e))