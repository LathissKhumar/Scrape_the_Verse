"""
A2A package export for Lead Manager.
"""

from .agent import a2a_router
from .skills import A2ASkillsHandler

__all__ = ["a2a_router", "A2ASkillsHandler"]
