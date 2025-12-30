from pydantic import BaseModel, Field


class GenerateBODataRequest(BaseModel):
    pivot_val: float = Field(default=0.5, ge=0, le=10)
    date: str
    start_from: int = Field(default=1, ge=1)
