import hashlib
import json
import base64
from typing import Dict, Any
from PIL import Image
import io
import os
from openai import OpenAI


class ModerationService:
    """Service for content moderation analysis using OpenAI's omni-moderation-latest"""

    # Initialize OpenAI client
    _client = None

    @classmethod
    def get_openai_client(cls) -> OpenAI:
        """Get or create OpenAI client"""
        if cls._client is None:
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY environment variable is not set")
            cls._client = OpenAI(api_key=api_key)
        return cls._client

    @staticmethod
    def generate_content_hash(content: str) -> str:
        """Generate SHA256 hash of content"""
        return hashlib.sha256(content.encode()).hexdigest()

    @staticmethod
    def generate_image_hash(image_bytes: bytes) -> str:
        """Generate SHA256 hash of image"""
        return hashlib.sha256(image_bytes).hexdigest()

    @classmethod
    def analyze_text(cls, text: str) -> Dict[str, Any]:
        """
        Analyze text content for inappropriate material using OpenAI's omni-moderation-latest.

        Uses OpenAI's latest multimodal moderation model that provides detailed
        category-level scores for various types of inappropriate content.
        """
        try:
            client = cls.get_openai_client()

            # Call OpenAI Moderation API
            response = client.moderations.create(
                model="omni-moderation-latest",
                input=text
            )

            result = response.results[0]

            # Get flagged categories
            flagged_categories = []
            category_scores = {}

            for category, flagged in result.categories.model_dump().items():
                score = getattr(result.category_scores, category)
                category_scores[category] = score
                if flagged:
                    flagged_categories.append(category)

            # Determine classification
            is_inappropriate = result.flagged
            classification = "inappropriate" if is_inappropriate else "appropriate"

            # Calculate overall confidence (max score across all categories)
            max_score = max(category_scores.values()) if category_scores else 0.0
            confidence = float(max_score)

            # Build reasoning
            if is_inappropriate:
                top_categories = sorted(
                    [(cat, score) for cat, score in category_scores.items()],
                    key=lambda x: x[1],
                    reverse=True
                )[:3]
                top_flags = [f"{cat.replace('_', ' ')} ({score:.2%})" for cat, score in top_categories if score > 0.1]
                reasoning = f"OpenAI detected inappropriate content. Flagged categories: {', '.join(flagged_categories)}. Top scores: {', '.join(top_flags)}"
            else:
                reasoning = "OpenAI analysis indicates appropriate content. No policy violations detected."

            llm_response = json.dumps({
                "model": "omni-moderation-latest",
                "flagged": is_inappropriate,
                "categories": result.categories.model_dump(),
                "category_scores": category_scores,
                "text_length": len(text)
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
                "reasoning": f"Error analyzing text: {str(e)}",
                "llm_response": json.dumps({"error": str(e)})
            }

    @classmethod
    def analyze_image(cls, image_bytes: bytes) -> Dict[str, Any]:
        """
        Analyze image content for inappropriate material using OpenAI's omni-moderation-latest.

        Uses OpenAI's latest multimodal moderation model that can analyze images
        for various types of inappropriate content including violence, sexual content, etc.
        """
        try:
            # Open and validate image
            image = Image.open(io.BytesIO(image_bytes))
            width, height = image.size
            format_type = image.format

            # Convert to RGB if necessary (required for consistent encoding)
            if image.mode != "RGB":
                image = image.convert("RGB")

            # Convert image back to bytes in a consistent format
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='PNG')
            img_byte_arr = img_byte_arr.getvalue()

            # Encode image to base64
            base64_image = base64.b64encode(img_byte_arr).decode('utf-8')

            # Create data URL for the image
            image_url = f"data:image/png;base64,{base64_image}"

            client = cls.get_openai_client()

            # Call OpenAI Moderation API with image
            response = client.moderations.create(
                model="omni-moderation-latest",
                input=[
                    {"type": "image_url", "image_url": {"url": image_url}}
                ]
            )

            result = response.results[0]

            # Get flagged categories
            flagged_categories = []
            category_scores = {}

            for category, flagged in result.categories.model_dump().items():
                score = getattr(result.category_scores, category)
                category_scores[category] = score
                if flagged:
                    flagged_categories.append(category)

            # Determine classification
            is_inappropriate = result.flagged
            classification = "inappropriate" if is_inappropriate else "appropriate"

            # Calculate overall confidence (max score across all categories)
            max_score = max(category_scores.values()) if category_scores else 0.0
            confidence = float(max_score)

            # Build reasoning
            if is_inappropriate:
                top_categories = sorted(
                    [(cat, score) for cat, score in category_scores.items()],
                    key=lambda x: x[1],
                    reverse=True
                )[:3]
                top_flags = [f"{cat.replace('_', ' ')} ({score:.2%})" for cat, score in top_categories if score > 0.1]
                reasoning = f"OpenAI detected inappropriate image content. Flagged categories: {', '.join(flagged_categories)}. Top scores: {', '.join(top_flags)}"
            else:
                reasoning = "OpenAI analysis indicates appropriate image content. No policy violations detected."

            llm_response = json.dumps({
                "model": "omni-moderation-latest",
                "flagged": is_inappropriate,
                "categories": result.categories.model_dump(),
                "category_scores": category_scores,
                "dimensions": {"width": width, "height": height},
                "format": format_type
            })

            return {
                "classification": classification,
                "confidence": float(confidence),
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
