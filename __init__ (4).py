from app.routers.auth import router as auth_router
from app.routers.incidents import router as incidents_router
from app.routers.sos import router as sos_router
from app.routers.map import router as map_router
from app.routers.notifications import router as notifications_router
from app.routers.dashboard import router as dashboard_router
from app.routers.authority import router as authority_router

__all__ = [
    "auth_router",
    "incidents_router",
    "sos_router",
    "map_router",
    "notifications_router",
    "dashboard_router",
    "authority_router"
]
