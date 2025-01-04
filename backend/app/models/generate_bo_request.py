from pydantic import BaseModel


class GenerateBODataRequest(BaseModel):
    pivot_val: float
    date: str
