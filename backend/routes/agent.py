import logging

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from services.agent_service import run_hiring_agent


if not logging.getLogger().handlers:
    logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)


router = APIRouter(tags=["Agent"])


class JobDescriptionRequest(BaseModel):
    job_description: str
    num_candidates: int = Field(default=3, ge=1)


@router.post("/api/agent/screen")
async def screen_candidates(payload: JobDescriptionRequest) -> dict:
    try:
        evaluation = await run_hiring_agent(
            job_description=payload.job_description,
            num_candidates=payload.num_candidates,
        )
        return {"evaluation": evaluation}
    except Exception as exc:
        logger.exception("Hiring screen agent execution failed.")
        raise HTTPException(
            status_code=500,
            detail={"message": "Failed to run hiring screen agent."},
        ) from exc
