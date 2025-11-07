from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.connection import get_db
from schemas.moderation import TextModerationRequest, ModerationResponse
from models.moderation import ModerationRequest, ModerationResult
from services.moderation_service import ModerationService

router = APIRouter(prefix="/api/text", tags=["Text Moderation"])


@router.post("/moderate", response_model=ModerationResponse)
async def moderate_text(
    request: TextModerationRequest,
    db: Session = Depends(get_db)
):
    """
    Moderate text content for inappropriate material.

    This endpoint:
    1. Creates a moderation request
    2. Analyzes the text content
    3. Stores the results in the database
    4. Returns the request ID and status
    """
    try:
        # Generate content hash
        content_hash = ModerationService.generate_content_hash(request.text)

        # Create moderation request
        moderation_request = ModerationRequest(
            content_type="text",
            content_hash=content_hash,
            status="pending"
        )
        db.add(moderation_request)
        db.commit()
        db.refresh(moderation_request)

        # Analyze text
        analysis_result = ModerationService.analyze_text(request.text)

        # Create moderation result
        moderation_result = ModerationResult(
            request_id=moderation_request.id,
            classification=analysis_result["classification"],
            confidence=analysis_result["confidence"],
            reasoning=analysis_result["reasoning"],
            llm_response=analysis_result["llm_response"]
        )
        db.add(moderation_result)

        # Update request status
        moderation_request.status = "completed"
        db.commit()

        return ModerationResponse(
            request_id=moderation_request.id,
            status="completed",
            message=f"Text moderation completed. Classification: {analysis_result['classification']}"
        )

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error processing text moderation: {str(e)}")
