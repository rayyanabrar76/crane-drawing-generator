"""Input rules for a crane design. The server checks these on every save.

Crane type: single girder overhead (EOT) crane, like the reference drawing.
All lengths in millimetres (mm), like the reference drawing.

Ranges are ESTIMATES (my assumptions), not from a standard.
The reference drawing shows: 10 t load, 25000 mm span, 7900 mm lifting height.
"""
from pydantic import BaseModel, Field


class CraneInputs(BaseModel):
    capacity_t: float = Field(..., ge=1, le=20, description="Load in tonnes. Estimate: 1-20 t")
    span_mm: int = Field(..., ge=5000, le=30000, description="Rail centre to rail centre. Estimate: 5-30 m")
    lifting_height_mm: int = Field(..., ge=3000, le=20000, description="Floor to hook top. Estimate: 3-20 m")


class DesignIn(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    inputs: CraneInputs
