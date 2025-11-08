from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from database.connection import get_db
from models.moderation import ModerationRequest, ModerationResult
from schemas.moderation import (
    AnalyticsSummary,
    ContentTypeBreakdown,
    ClassificationBreakdown,
    StatusBreakdown
)
from datetime import datetime

router = APIRouter(prefix="/api/v1/analytics", tags=["Analytics"])


@router.get("/summary", response_model=AnalyticsSummary)
async def get_analytics_summary(
    user: str = Query(..., description="User email address"),
    db: Session = Depends(get_db)
):
    """
    Get analytics summary for a specific user.

    This endpoint aggregates moderation data for a user including:
    - Total number of moderation requests
    - Breakdown by content type (text/image)
    - Breakdown by classification (appropriate/inappropriate)
    - Breakdown by status (pending/completed/failed)
    - Average confidence score
    - Date range of requests

    Args:
        user: Email address of the user
        db: Database session

    Returns:
        AnalyticsSummary: Aggregated analytics data for the user
    """
    try:
        # Get all moderation requests for the user
        user_requests = db.query(ModerationRequest).filter(
            ModerationRequest.user_email == user
        ).all()

        if not user_requests:
            raise HTTPException(
                status_code=404,
                detail=f"No moderation requests found for user: {user}"
            )

        # Initialize counters
        total_requests = len(user_requests)
        content_type_counts = {"text": 0, "image": 0}
        status_counts = {"pending": 0, "completed": 0, "failed": 0}
        classification_counts = {"appropriate": 0, "inappropriate": 0}
        confidence_scores = []

        # Get request IDs for joining with results
        request_ids = [req.id for req in user_requests]

        # Get all moderation results for these requests
        results = db.query(ModerationResult).filter(
            ModerationResult.request_id.in_(request_ids)
        ).all()

        # Create a mapping of request_id to result
        results_map = {result.request_id: result for result in results}

        # Aggregate data
        for request in user_requests:
            # Count content types
            if request.content_type in content_type_counts:
                content_type_counts[request.content_type] += 1

            # Count statuses
            if request.status in status_counts:
                status_counts[request.status] += 1

            # Get result for this request if it exists
            result = results_map.get(request.id)
            if result:
                # Count classifications
                if result.classification in classification_counts:
                    classification_counts[result.classification] += 1

                # Collect confidence scores
                if result.confidence is not None:
                    confidence_scores.append(result.confidence)

        # Calculate average confidence
        average_confidence = None
        if confidence_scores:
            average_confidence = sum(confidence_scores) / len(confidence_scores)

        # Get date range
        dates = [req.created_at for req in user_requests if req.created_at]
        first_request_date = min(dates) if dates else None
        last_request_date = max(dates) if dates else None

        # Build response
        return AnalyticsSummary(
            user_email=user,
            total_requests=total_requests,
            content_type_breakdown=ContentTypeBreakdown(
                text=content_type_counts["text"],
                image=content_type_counts["image"]
            ),
            classification_breakdown=ClassificationBreakdown(
                appropriate=classification_counts["appropriate"],
                inappropriate=classification_counts["inappropriate"]
            ),
            status_breakdown=StatusBreakdown(
                pending=status_counts["pending"],
                completed=status_counts["completed"],
                failed=status_counts["failed"]
            ),
            average_confidence=average_confidence,
            first_request_date=first_request_date,
            last_request_date=last_request_date
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving analytics: {str(e)}"
        )
