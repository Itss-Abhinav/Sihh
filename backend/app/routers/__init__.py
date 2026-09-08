from backend.app.routers.auth import router as auth_router
from backend.app.routers.scans import router as scans_router
from backend.app.routers.rules import router as rules_router
from backend.app.routers.admin import router as admin_router

__all__ = ["auth_router", "scans_router", "rules_router", "admin_router"]
