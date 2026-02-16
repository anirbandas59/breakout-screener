"""Enum routes — expose backend indicator enum values to clients."""
from fastapi import APIRouter

from app.models.enums import BreakoutIndicator, CandleIndicator, VolumeIndicator
from app.models.schemas import EnumsResponse

router = APIRouter(tags=["enums"])


@router.get("/enums", response_model=EnumsResponse)
def get_enums():
    """
    Return all indicator enum values used in breakout analysis.

    Clients should use these values for filter options and display labels
    instead of hardcoding them, ensuring frontend stays in sync with backend.
    """
    return {
        "breakout_indicators": [e.value for e in BreakoutIndicator],
        "candle_indicators": [e.value for e in CandleIndicator],
        "volume_indicators": [e.value for e in VolumeIndicator],
    }
