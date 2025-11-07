import hashlib
import json
from typing import Dict, Any, Optional
from PIL import Image
import io
import torch
from transformers import CLIPProcessor, CLIPModel


class ModerationService:
    """Service for content moderation analysis"""

    # Define inappropriate keywords for text moderation (basic example)
    INAPPROPRIATE_KEYWORDS = [
        "violence", "hate", "explicit", "abuse", "threat"
        # Add more keywords as needed
    ]

    # CLIP model and processor (lazy loading)
    _clip_model: Optional[CLIPModel] = None
    _clip_processor: Optional[CLIPProcessor] = None

    # Content categories for CLIP-based image moderation
    INAPPROPRIATE_CATEGORIES = [
        "violent content",
        "graphic violence",
        "explicit sexual content",
        "nudity",
        "hate symbols",
        "offensive gestures",
        "weapons",
        "blood and gore",
        "drug use",
        "self-harm"
    ]

    APPROPRIATE_CATEGORIES = [
        "safe content",
        "family-friendly image",
        "appropriate content",
        "workplace appropriate"
    ]

    @classmethod
    def load_clip_model(cls):
        """Lazy load CLIP model and processor"""
        if cls._clip_model is None:
            print("Loading CLIP model...")
            cls._clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
            cls._clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
            print("CLIP model loaded successfully")
        return cls._clip_model, cls._clip_processor

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

    @classmethod
    def analyze_image(cls, image_bytes: bytes) -> Dict[str, Any]:
        """
        Analyze image content for inappropriate material using CLIP.

        Uses OpenAI's CLIP model to perform zero-shot classification
        by comparing the image against text descriptions of inappropriate
        and appropriate content categories.
        """
        try:
            # Open and validate image
            image = Image.open(io.BytesIO(image_bytes))
            width, height = image.size
            format_type = image.format

            # Convert to RGB if necessary
            if image.mode != "RGB":
                image = image.convert("RGB")

            # Load CLIP model
            model, processor = cls.load_clip_model()

            # Prepare all category labels
            all_categories = cls.INAPPROPRIATE_CATEGORIES + cls.APPROPRIATE_CATEGORIES

            # Process image and text
            inputs = processor(
                text=all_categories,
                images=image,
                return_tensors="pt",
                padding=True
            )

            # Get predictions
            with torch.no_grad():
                outputs = model(**inputs)
                logits_per_image = outputs.logits_per_image
                probs = logits_per_image.softmax(dim=1)

            # Get scores for each category
            scores = probs[0].tolist()
            category_scores = {cat: score for cat, score in zip(all_categories, scores)}

            # Calculate inappropriate and appropriate scores
            inappropriate_score = sum(
                category_scores[cat] for cat in cls.INAPPROPRIATE_CATEGORIES
            )
            appropriate_score = sum(
                category_scores[cat] for cat in cls.APPROPRIATE_CATEGORIES
            )

            # Find top flagged categories
            inappropriate_matches = sorted(
                [(cat, category_scores[cat]) for cat in cls.INAPPROPRIATE_CATEGORIES],
                key=lambda x: x[1],
                reverse=True
            )[:3]

            # Determine classification
            # Using a threshold: if inappropriate score is higher and significant
            threshold = 0.3
            is_inappropriate = (
                inappropriate_score > appropriate_score and
                inappropriate_matches[0][1] > threshold
            )

            classification = "inappropriate" if is_inappropriate else "appropriate"
            confidence = max(inappropriate_score, appropriate_score)

            # Build reasoning
            if is_inappropriate:
                top_flags = [f"{cat} ({score:.2%})" for cat, score in inappropriate_matches if score > 0.1]
                reasoning = f"CLIP detected potential inappropriate content. Top matches: {', '.join(top_flags)}"
            else:
                reasoning = f"CLIP analysis indicates appropriate content (confidence: {appropriate_score:.2%})"

            llm_response = json.dumps({
                "model": "CLIP (openai/clip-vit-base-patch32)",
                "inappropriate_score": round(inappropriate_score, 4),
                "appropriate_score": round(appropriate_score, 4),
                "top_inappropriate_matches": [
                    {"category": cat, "score": round(score, 4)}
                    for cat, score in inappropriate_matches
                ],
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
