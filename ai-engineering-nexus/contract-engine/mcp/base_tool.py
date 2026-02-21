from abc import ABC, abstractmethod

from pydantic import BaseModel

class ToolBase(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        """The unique identifier for every tool"""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Explains to the LLM what the tool does"""
        pass

    @property
    @abstractmethod
    def args_schema(self) -> type[BaseModel]:
        """List of params the tool needs to run"""
        pass

    @abstractmethod
    async def execute(self, **kwargs) -> str:
        """The actual execution logic of the tool"""
        pass