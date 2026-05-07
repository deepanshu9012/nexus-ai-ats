from fastapi import APIRouter

from schemas.responses import HealthResponse
from services.health_service import get_health_status


router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    return HealthResponse(**get_health_status())
