import hashlib
import json
import base64
from typing import Dict, Any
from PIL import Image
import io
import os
import vertexai
from vertexai.generative_models import GenerativeModel, Part, SafetySetting, HarmCategory, HarmBlockThreshold


class ModerationService:
    """Service for content moderation analysis using Google Vertex AI Gemini"""

    # Initialize Vertex AI
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
    def initialize_vertex_ai(cls):
        """Initialize Vertex AI with project credentials"""
        if not cls._initialized:
            project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
            location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")

            if not project_id:
                raise ValueError("GOOGLE_CLOUD_PROJECT environment variable is not set")

            vertexai.init(project=project_id, location=location)
            cls._initialized = True
            print(f"✓ Vertex AI initialized (project: {project_id}, location: {location})")

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
        Analyze text content for inappropriate material using Vertex AI Gemini.

        Uses Google's Gemini model with safety filters to detect harmful content
        across multiple categories including hate speech, harassment, dangerous
        content, and sexually explicit material.
        """
        try:
            cls.initialize_vertex_ai()

            # Initialize Gemini model
            model = GenerativeModel("gemini-1.5-flash")

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

            # Generate response with safety settings
            response = model.generate_content(
                moderation_prompt,
                safety_settings={
                    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                }
            )

            # Extract safety ratings
            safety_ratings = {}
            flagged_categories = []
            max_score = 0.0

            if hasattr(response, 'candidates') and response.candidates:
                for rating in response.candidates[0].safety_ratings:
                    category_name = cls.HARM_CATEGORIES.get(rating.category.name, rating.category.name)
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

            if hasattr(response, 'text'):
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
                "model": "gemini-1.5-flash",
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
        Analyze image content for inappropriate material using Vertex AI Gemini.

        Uses Google's Gemini multimodal model with safety filters to detect
        harmful visual content across multiple categories.
        """
        try:
            cls.initialize_vertex_ai()

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

            # Encode to base64
            base64_image = base64.b64encode(img_byte_arr).decode('utf-8')

            # Initialize Gemini model
            model = GenerativeModel("gemini-1.5-flash")

            # Create image part
            image_part = Part.from_data(img_byte_arr, mime_type="image/png")

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

            # Generate response with safety settings
            response = model.generate_content(
                [image_part, moderation_prompt],
                safety_settings={
                    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                }
            )

            # Extract safety ratings
            safety_ratings = {}
            flagged_categories = []
            max_score = 0.0

            if hasattr(response, 'candidates') and response.candidates:
                for rating in response.candidates[0].safety_ratings:
                    category_name = cls.HARM_CATEGORIES.get(rating.category.name, rating.category.name)
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

            if hasattr(response, 'text'):
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
                "model": "gemini-1.5-flash",
                "safety_ratings": safety_ratings,
                "flagged_categories": flagged_categories,
                "gemini_analysis": gemini_analysis[:500],
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
