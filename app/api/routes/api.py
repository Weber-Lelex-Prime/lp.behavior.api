from fastapi import APIRouter

from app.api.routes import lambdas

router = APIRouter()
router.include_router(lambdas.router, tags=["lambdas"], prefix="/lambdas")
