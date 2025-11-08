import hashlib
import json
import base64
from typing import Dict, Any
from PIL import Image
import io
import os
import google.generativeai as genai


class ModerationService:
    """Service for content moderation analysis using Google Gemini API"""

    # Initialize Gemini API
    _initialized = False

    # Safety categories mapping
    HARM_CATEGORIES = {
        "HARM_CATEGORY_HATE_SPEECH": "hate_speech",
        "HARM_CATEGORY_DANGEROUS_CONTENT": "dangerous_content",
        "HARM_CATEGORY_HARASSMENT": "harassment",
        "HARM_CATEGORY_SEXUALLY_EXPLICIT": "sexually_explicit"
    }

    # Harm probability levels (higher number = more likely to be harmful)
    HARM_PROBABILITY_SCORES = {
        "NEGLIGIBLE": 0.1,
        "LOW": 0.3,
        "MEDIUM": 0.6,
        "HIGH": 0.9
    }

    @classmethod
    def initialize_gemini(cls):
        """Initialize Gemini API with API key"""
        if not cls._initialized:
            api_key = os.getenv("GOOGLE_API_KEY")

            if not api_key:
                raise ValueError("GOOGLE_API_KEY environment variable is not set")

            genai.configure(api_key=api_key)
            cls._initialized = True
            print(f"✓ Gemini API initialized")

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
        Analyze text content for inappropriate material using Google Gemini API.

        Uses Google's Gemini model with safety filters to detect harmful content
        across multiple categories including hate speech, harassment, dangerous
        content, and sexually explicit material.
        """
        try:
            cls.initialize_gemini()

            # Initialize Gemini model
            model = genai.GenerativeModel("gemini-flash-latest")

            # Create moderation prompt
            moderation_prompt = f"""Analyze the following text for inappropriate content.
Provide a detailed assessment of whether it contains:
- Hate speech or discriminatory content
- Harassment or bullying
- Dangerous or harmful content
- Sexually explicit material
- Violence or graphic content

Text to analyze: "{text}"

Respond with a JSON object containing:
- "is_appropriate": boolean
- "flagged_categories": list of categories that are problematic
- "reasoning": brief explanation of your assessment
"""

            # Set safety settings to BLOCK_NONE to get ratings without blocking
            safety_settings = [
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            ]

            # Generate response
            response = model.generate_content(
                moderation_prompt,
                safety_settings=safety_settings
            )

            # Extract safety ratings
            safety_ratings = {}
            flagged_categories = []
            max_score = 0.0

            if hasattr(response, 'candidates') and response.candidates:
                for rating in response.candidates[0].safety_ratings:
                    category_name = cls.HARM_CATEGORIES.get(
                        rating.category.name,
                        rating.category.name
                    )
                    probability = rating.probability.name
                    score = cls.HARM_PROBABILITY_SCORES.get(probability, 0.0)

                    safety_ratings[category_name] = {
                        "probability": probability,
                        "score": score
                    }

                    max_score = max(max_score, score)

                    # Flag if MEDIUM or HIGH probability
                    if probability in ["MEDIUM", "HIGH"]:
                        flagged_categories.append(category_name)

            # Try to parse Gemini's response
            gemini_analysis = ""
            is_appropriate_by_content = True

            if hasattr(response, 'text') and response.text:
                gemini_analysis = response.text
                # Simple heuristic: if Gemini response mentions problems
                if any(word in gemini_analysis.lower() for word in ["inappropriate", "problematic", "flagged", "harmful"]):
                    is_appropriate_by_content = False

            # Determine final classification
            is_inappropriate = len(flagged_categories) > 0 or not is_appropriate_by_content
            classification = "inappropriate" if is_inappropriate else "appropriate"
            confidence = float(max_score) if max_score > 0 else 0.85

            # Build reasoning
            if is_inappropriate:
                reasoning = f"Gemini detected potentially inappropriate content. "
                if flagged_categories:
                    reasoning += f"Flagged safety categories: {', '.join(flagged_categories)}. "
                reasoning += "Content requires review."
            else:
                reasoning = "Gemini analysis indicates appropriate content. No safety concerns detected."

            llm_response = json.dumps({
                "model": "gemini-flash-latest",
                "safety_ratings": safety_ratings,
                "flagged_categories": flagged_categories,
                "gemini_analysis": gemini_analysis[:500],  # Truncate for storage
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
        Analyze image content for inappropriate material using Google Gemini API.

        Uses Google's Gemini multimodal model with safety filters to detect
        harmful visual content across multiple categories.
        """
        try:
            cls.initialize_gemini()

            # Open and validate image
            image = Image.open(io.BytesIO(image_bytes))
            width, height = image.size
            format_type = image.format

            # Convert to RGB if necessary
            if image.mode != "RGB":
                image = image.convert("RGB")

            # Convert image back to bytes
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='PNG')
            img_byte_arr = img_byte_arr.getvalue()

            # Initialize Gemini model
            model = genai.GenerativeModel("gemini-flash-latest")

            # Upload image
            uploaded_file = genai.upload_file(io.BytesIO(img_byte_arr), mime_type="image/png")

            # Create moderation prompt for image
            moderation_prompt = """Analyze this image for inappropriate content.
Assess whether it contains:
- Hate speech symbols or discriminatory imagery
- Harassment or bullying depictions
- Dangerous, violent, or harmful content
- Sexually explicit or inappropriate material
- Graphic violence or disturbing imagery

Provide a JSON response with:
- "is_appropriate": boolean
- "flagged_categories": list of problematic categories
- "reasoning": brief explanation
"""

            # Set safety settings
            safety_settings = [
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            ]

            # Generate response
            response = model.generate_content(
                [uploaded_file, moderation_prompt],
                safety_settings=safety_settings
            )

            # Extract safety ratings
            safety_ratings = {}
            flagged_categories = []
            max_score = 0.0

            if hasattr(response, 'candidates') and response.candidates:
                for rating in response.candidates[0].safety_ratings:
                    category_name = cls.HARM_CATEGORIES.get(
                        rating.category.name,
                        rating.category.name
                    )
                    probability = rating.probability.name
                    score = cls.HARM_PROBABILITY_SCORES.get(probability, 0.0)

                    safety_ratings[category_name] = {
                        "probability": probability,
                        "score": score
                    }

                    max_score = max(max_score, score)

                    # Flag if MEDIUM or HIGH probability
                    if probability in ["MEDIUM", "HIGH"]:
                        flagged_categories.append(category_name)

            # Try to parse Gemini's response
            gemini_analysis = ""
            is_appropriate_by_content = True

            if hasattr(response, 'text') and response.text:
                gemini_analysis = response.text
                if any(word in gemini_analysis.lower() for word in ["inappropriate", "problematic", "flagged", "harmful"]):
                    is_appropriate_by_content = False

            # Determine final classification
            is_inappropriate = len(flagged_categories) > 0 or not is_appropriate_by_content
            classification = "inappropriate" if is_inappropriate else "appropriate"
            confidence = float(max_score) if max_score > 0 else 0.85

            # Build reasoning
            if is_inappropriate:
                reasoning = f"Gemini detected potentially inappropriate image content. "
                if flagged_categories:
                    reasoning += f"Flagged safety categories: {', '.join(flagged_categories)}. "
                reasoning += "Image requires review."
            else:
                reasoning = "Gemini analysis indicates appropriate image content. No safety concerns detected."

            llm_response = json.dumps({
                "model": "gemini-flash-latest",
                "safety_ratings": safety_ratings,
                "flagged_categories": flagged_categories,
                "gemini_analysis": gemini_analysis[:500],
                "dimensions": {"width": width, "height": height},
                "format": format_type
            })

            # Clean up uploaded file
            try:
                genai.delete_file(uploaded_file.name)
            except:
                pass  # Ignore cleanup errors

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
