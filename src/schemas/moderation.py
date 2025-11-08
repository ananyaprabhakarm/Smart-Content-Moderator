from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class TextModerationRequest(BaseModel):
    text: str = Field(..., description="Text content to moderate")
    content_id: Optional[str] = Field(None, description="Optional identifier for the content")
    user_email: Optional[str] = Field(None, description="Email of the user submitting the content")


class ImageModerationRequest(BaseModel):
    content_id: Optional[str] = Field(None, description="Optional identifier for the content")
    user_email: Optional[str] = Field(None, description="Email of the user submitting the content")


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
    user_email: Optional[str] = None
    status: str
    created_at: datetime
    result: Optional[ModerationResultDetail] = None

    class Config:
        from_attributes = True


class AnalysisSummaryListResponse(BaseModel):
    total: int
    summaries: List[AnalysisSummaryResponse]


class ContentTypeBreakdown(BaseModel):
    text: int = 0
    image: int = 0


class ClassificationBreakdown(BaseModel):
    appropriate: int = 0
    inappropriate: int = 0


class StatusBreakdown(BaseModel):
    pending: int = 0
    completed: int = 0
    failed: int = 0


class AnalyticsSummary(BaseModel):
    user_email: str
    total_requests: int
    content_type_breakdown: ContentTypeBreakdown
    classification_breakdown: ClassificationBreakdown
    status_breakdown: StatusBreakdown
    average_confidence: Optional[float] = None
    first_request_date: Optional[datetime] = None
    last_request_date: Optional[datetime] = None

    class Config:
        from_attributes = True
