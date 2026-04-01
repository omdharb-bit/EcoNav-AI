from __future__ import annotations

from fastapi import APIRouter

from packages.env_core.core.grader import grade_exposure

router = APIRouter(prefix="/env-core", tags=["env-core"])


@router.get("/grade/{exposure}")
def get_exposure_grade(exposure: float) -> dict[str, str | float]:
    return {"exposure": exposure, "grade": grade_exposure(exposure)}
