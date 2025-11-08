from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from database.connection import get_db
from schemas.moderation import ModerationResponse
from models.moderation import ModerationRequest, ModerationResult, NotificationLog
from services.moderation_service import ModerationService
from services.notification_service import NotificationService
from typing import Optional
import json

router = APIRouter(prefix="/api/image", tags=["Image Moderation"])


@router.post("/moderate", response_model=ModerationResponse)
async def moderate_image(
    image: UploadFile = File(..., description="Image file to moderate"),
    content_id: Optional[str] = Form(None, description="Optional identifier for the content"),
    db: Session = Depends(get_db)
):
    """
    Moderate image content for inappropriate material.

    This endpoint:
    1. Accepts an uploaded image file
    2. Creates a moderation request
    3. Analyzes the image content
    4. Stores the results in the database
    5. Returns the request ID and status
    """
    try:
        # Validate image file type
        allowed_types = ["image/jpeg", "image/jpg", "image/png", "image/gif", "image/webp"]
        if image.content_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Allowed types: {', '.join(allowed_types)}"
            )

        # Read image bytes
        image_bytes = await image.read()

        # Generate content hash
        content_hash = ModerationService.generate_image_hash(image_bytes)

        # Create moderation request
        moderation_request = ModerationRequest(
            content_type="image",
            content_hash=content_hash,
            status="pending"
        )
        db.add(moderation_request)
        db.commit()
        db.refresh(moderation_request)

        # Analyze image
        analysis_result = ModerationService.analyze_image(image_bytes)

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
        moderation_request.status = "completed" if analysis_result["classification"] != "error" else "failed"
        db.commit()

        # Send notifications if inappropriate content is detected
        if analysis_result["classification"] == "inappropriate":
            try:
                # Extract flagged categories from LLM response
                flagged_categories = []
                if analysis_result.get("llm_response"):
                    try:
                        llm_data = json.loads(analysis_result["llm_response"])
                        flagged_categories = llm_data.get("flagged_categories", [])
                    except json.JSONDecodeError:
                        pass

                # Send notifications via all channels
                notification_results = await NotificationService.notify_inappropriate_content(
                    request_id=moderation_request.id,
                    content_type="image",
                    classification=analysis_result["classification"],
                    confidence=analysis_result["confidence"],
                    reasoning=analysis_result["reasoning"],
                    flagged_categories=flagged_categories
                )

                # Log notification results to database
                for channel, result in notification_results.items():
                    if result and result["status"] != "skipped":
                        notification_log = NotificationLog(
                            request_id=moderation_request.id,
                            channel=channel,
                            status=result["status"]
                        )
                        db.add(notification_log)

                db.commit()

            except Exception as notification_error:
                # Log notification error but don't fail the moderation request
                print(f"Notification error: {str(notification_error)}")

        return ModerationResponse(
            request_id=moderation_request.id,
            status=moderation_request.status,
            message=f"Image moderation completed. Classification: {analysis_result['classification']}"
        )

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error processing image moderation: {str(e)}")
