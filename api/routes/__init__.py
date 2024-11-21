from fastapi import APIRouter
from .routes import routes_router as apiRoutes

router = APIRouter(
    prefix="/api",
)

router.include_router(apiRoutes)
