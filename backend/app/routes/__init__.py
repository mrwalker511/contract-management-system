"""
Routes package
"""
from .auth import router as auth_router
from .users import router as users_router
from .templates import router as templates_router
from .contracts import router as contracts_router

__all__ = ["auth_router", "users_router", "templates_router", "contracts_router"]
