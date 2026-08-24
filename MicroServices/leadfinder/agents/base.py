from abc import ABC

from leadfinder.config.logging import get_logger


class BaseAgent(ABC):
    """Base class for all multi-agent components."""

    def __init__(self, name: str):
        self.name = name
        self.logger = get_logger(name.upper())

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} name='{self.name}'>"
