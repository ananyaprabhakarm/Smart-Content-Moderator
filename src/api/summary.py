from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from database.connection import get_db
from schemas.moderation import AnalysisSummaryResponse, AnalysisSummaryListResponse, ModerationResultDetail
from models.moderation import ModerationRequest, ModerationResult
from typing import Optional

router = APIRouter(prefix="/api/summary", tags=["Analysis Summary"])


@router.get("/{request_id}", response_model=AnalysisSummaryResponse)
async def get_analysis_summary(
    request_id: int,
    db: Session = Depends(get_db)
):
    """
    Get analysis summary for a specific moderation request.

    This endpoint retrieves:
    - Request details (ID, content type, hash, status, timestamp)
    - Moderation result (classification, confidence, reasoning)
    """
    # Get moderation request
    moderation_request = db.query(ModerationRequest).filter(
        ModerationRequest.id == request_id
    ).first()

    if not moderation_request:
        raise HTTPException(status_code=404, detail="Moderation request not found")

    # Get moderation result
    moderation_result = db.query(ModerationResult).filter(
        ModerationResult.request_id == request_id
    ).first()

    result_detail = None
    if moderation_result:
        result_detail = ModerationResultDetail(
            classification=moderation_result.classification,
            confidence=moderation_result.confidence,
            reasoning=moderation_result.reasoning
        )

    return AnalysisSummaryResponse(
        request_id=moderation_request.id,
        content_type=moderation_request.content_type,
        content_hash=moderation_request.content_hash,
        status=moderation_request.status,
        created_at=moderation_request.created_at,
        result=result_detail
    )


@router.get("", response_model=AnalysisSummaryListResponse)
async def get_analysis_summaries(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of records to return"),
    content_type: Optional[str] = Query(None, description="Filter by content type (text/image)"),
    status: Optional[str] = Query(None, description="Filter by status (pending/completed/failed)"),
    db: Session = Depends(get_db)
):
    """
    Get a paginated list of analysis summaries.

    This endpoint supports:
    - Pagination (skip and limit parameters)
    - Filtering by content type
    - Filtering by status
    """
    # Build query
    query = db.query(ModerationRequest)

    # Apply filters
    if content_type:
        query = query.filter(ModerationRequest.content_type == content_type)
    if status:
        query = query.filter(ModerationRequest.status == status)

    # Get total count
    total = query.count()

    # Get paginated results
    moderation_requests = query.order_by(
        desc(ModerationRequest.created_at)
    ).offset(skip).limit(limit).all()

    # Build response
    summaries = []
    for request in moderation_requests:
        # Get associated result
        result = db.query(ModerationResult).filter(
            ModerationResult.request_id == request.id
        ).first()

        result_detail = None
        if result:
            result_detail = ModerationResultDetail(
                classification=result.classification,
                confidence=result.confidence,
                reasoning=result.reasoning
            )

        summaries.append(AnalysisSummaryResponse(
            request_id=request.id,
            content_type=request.content_type,
            content_hash=request.content_hash,
            status=request.status,
            created_at=request.created_at,
            result=result_detail
        ))

    return AnalysisSummaryListResponse(
        total=total,
        summaries=summaries
    )
