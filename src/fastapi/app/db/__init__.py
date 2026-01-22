"""
Database integration layer
"""

from .dynamodb import get_dynamodb_client, init_dynamodb
from .repositories import CallEventRepository, ResidentRepository, UserRepository

__all__ = [
    "get_dynamodb_client",
    "init_dynamodb", 
    "CallEventRepository",
    "ResidentRepository",
    "UserRepository"
]