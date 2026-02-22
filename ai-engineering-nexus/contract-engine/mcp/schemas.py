from typing import Literal
from pydantic import BaseModel, Field
from base_tool import ToolBase
from weather import get_weather

class CalculatorArgs(BaseModel):
    a: float = Field(description="The first number")
    b: float = Field(description="The second number")
    operation: Literal["add", "subtract", "multiply", "divide"] = Field(description="The operation to perform")

class CalculatorTool(ToolBase):
    name = "perform_calculation"
    description = "A tool for performing basic arithmetic operations"
    args_schema = CalculatorArgs

    async def execute(self, a: float, b: float, operation: str) -> str:
        if operation == 'add':
            return str(a+b)
        elif operation == 'subtract':
            return str(a-b)
        elif operation == 'multiply':
            return str(a*b)
        elif operation == 'divide':
            return str(a/b) if b!=0 else 'Error: Division by zero'

class WeatherArgs(BaseModel):
    city: str = Field(description="Name of the city for which weather is to be checked.")

class WeatherTool(ToolBase):
    name = "get_weather"
    description = "A tool for getting current weather info"
    args_schema = WeatherArgs

    async def execute(self, city: str) -> dict:
        return get_weather(city)
        