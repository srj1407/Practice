from pydantic import BaseModel, HttpUrl, Field, field_validator
from typing import List, Annotated, Literal, Any

class Metadata(BaseModel):
    model: str | None = None
    tokens: int | None = None

class AgentResponse(BaseModel):
    """Agent Response schema"""
    answer: str
    confidence: float
    sources: Annotated[List[HttpUrl] | None, Field(min_length=1)] = None
    metadata: Metadata | None = None

    @field_validator('confidence')
    @classmethod
    def check(cls, v: float) -> float:
        if not(v>=0 and v<=1):
            raise ValueError('Confidence should be between 0 and 1')
        return v

class Step(BaseModel):
    step: int
    action: str

class TaskBreakdown(BaseModel):
    """Break down tasks and list the steps along with the estimated time taken in seconds."""
    goal: str
    steps: Annotated[List[Step] | None, Field(min_length=1)] = None
    estimated_time: int

    @field_validator('steps')
    @classmethod
    def check(cls, v: List[Step]) -> List[Step]:
        if len(v) == 0:
            raise ValueError('Steps list cant be empty')
        return v

class Tool(BaseModel):
    tool_name: str
    parameters: dict[str, Any]
    reasoning: str | None = None

    @field_validator('tool_name')
    @classmethod
    def check(cls, v: str) -> str:
        if v not in ["add", "subtract", "multiply", "divide"]:
            raise ValueError('Incorrect tool name')
        return v
    
class ToolCall(BaseModel):
    """Tool Call schema"""
    tools: List[Tool]

    @field_validator('tools')
    @classmethod
    def check(cls, v: List[Tool]) -> List[Tool]:
        if len(v) == 0:
            raise ValueError('No tools')
        return v