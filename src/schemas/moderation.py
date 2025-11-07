from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class TextModerationRequest(BaseModel):
    text: str = Field(..., description="Text content to moderate")
    content_id: Optional[str] = Field(None, description="Optional identifier for the content")


class ImageModerationRequest(BaseModel):
    content_id: Optional[str] = Field(None, description="Optional identifier for the content")


class ModerationResponse(BaseModel):
    request_id: int
    status: str
    message: str

    class Config:
        from_attributes = True


class ModerationResultDetail(BaseModel):
    classification: str
    confidence: Optional[float]
    reasoning: Optional[str]

    class Config:
        from_attributes = True


class AnalysisSummaryResponse(BaseModel):
    request_id: int
    content_type: str
    content_hash: str
    status: str
    created_at: datetime
    result: Optional[ModerationResultDetail] = None

    class Config:
        from_attributes = True


class AnalysisSummaryListResponse(BaseModel):
    total: int
    summaries: List[AnalysisSummaryResponse]
