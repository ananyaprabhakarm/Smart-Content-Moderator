import hashlib
import json
from typing import Dict, Any
from PIL import Image
import io


class ModerationService:
    """Service for content moderation analysis"""

    # Define inappropriate keywords for text moderation (basic example)
    INAPPROPRIATE_KEYWORDS = [
        "violence", "hate", "explicit", "abuse", "threat"
        # Add more keywords as needed
    ]

    @staticmethod
    def generate_content_hash(content: str) -> str:
        """Generate SHA256 hash of content"""
        return hashlib.sha256(content.encode()).hexdigest()

    @staticmethod
    def generate_image_hash(image_bytes: bytes) -> str:
        """Generate SHA256 hash of image"""
        return hashlib.sha256(image_bytes).hexdigest()

    @staticmethod
    def analyze_text(text: str) -> Dict[str, Any]:
        """
        Analyze text content for inappropriate material.

        This is a basic implementation. In production, you would integrate with:
        - OpenAI Moderation API
        - Perspective API
        - Custom trained models
        - Claude API for analysis
        """
        text_lower = text.lower()
        flagged_words = []

        # Check for inappropriate keywords
        for keyword in ModerationService.INAPPROPRIATE_KEYWORDS:
            if keyword in text_lower:
                flagged_words.append(keyword)

        is_appropriate = len(flagged_words) == 0
        confidence = 0.95 if len(flagged_words) > 0 else 0.85

        classification = "appropriate" if is_appropriate else "inappropriate"
        reasoning = (
            f"No inappropriate content detected."
            if is_appropriate
            else f"Flagged keywords found: {', '.join(flagged_words)}"
        )

        llm_response = json.dumps({
            "analysis": "Basic keyword-based analysis",
            "flagged_terms": flagged_words,
            "text_length": len(text)
        })

        return {
            "classification": classification,
            "confidence": confidence,
            "reasoning": reasoning,
            "llm_response": llm_response
        }

    @staticmethod
    def analyze_image(image_bytes: bytes) -> Dict[str, Any]:
        """
        Analyze image content for inappropriate material.

        This is a basic implementation. In production, you would integrate with:
        - AWS Rekognition
        - Google Cloud Vision API
        - Azure Content Moderator
        - Custom trained models
        """
        try:
            # Open and validate image
            image = Image.open(io.BytesIO(image_bytes))
            width, height = image.size
            format_type = image.format

            # Basic image validation
            # In production, this would use AI models for actual content analysis
            is_appropriate = True
            confidence = 0.75

            classification = "appropriate" if is_appropriate else "inappropriate"
            reasoning = f"Image analyzed: {width}x{height} pixels, format: {format_type}"

            llm_response = json.dumps({
                "analysis": "Basic image validation",
                "dimensions": {"width": width, "height": height},
                "format": format_type
            })

            return {
                "classification": classification,
                "confidence": confidence,
                "reasoning": reasoning,
                "llm_response": llm_response
            }
        except Exception as e:
            return {
                "classification": "error",
                "confidence": 0.0,
                "reasoning": f"Error processing image: {str(e)}",
                "llm_response": json.dumps({"error": str(e)})
            }
