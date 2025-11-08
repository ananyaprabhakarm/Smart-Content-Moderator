#!/usr/bin/env python3
"""
Test script to verify Google Cloud Vertex AI connection and Gemini model.
Run this script to check if your Google Cloud credentials are working correctly.

Usage:
    python test_vertexai_api.py
"""

import os
from dotenv import load_dotenv
import vertexai
from vertexai.generative_models import GenerativeModel, Part, HarmCategory, HarmBlockThreshold

# Load environment variables
load_dotenv()

def test_vertex_ai_connection():
    """Test Vertex AI connection and Gemini model"""

    print("=" * 60)
    print("Google Cloud Vertex AI Connection Test")
    print("=" * 60)

    # Check if project ID exists
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
    if not project_id:
        print("❌ ERROR: GOOGLE_CLOUD_PROJECT not found in environment variables")
        print("\nPlease:")
        print("1. Copy .env.example to .env")
        print("2. Add your Google Cloud Project ID to the .env file")
        print("3. Set up Google Cloud credentials")
        return False

    print(f"✓ Project ID found: {project_id}")

    # Check credentials
    credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if credentials_path:
        print(f"✓ Credentials path: {credentials_path}")
        if not os.path.exists(credentials_path):
            print(f"⚠ WARNING: Credentials file not found at {credentials_path}")
            print("  Make sure the file exists or use default application credentials")
    else:
        print("ℹ Using default application credentials")

    # Get location
    location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
    print(f"✓ Location: {location}")

    # Initialize Vertex AI
    try:
        vertexai.init(project=project_id, location=location)
        print("✓ Vertex AI initialized successfully")
    except Exception as e:
        print(f"❌ ERROR initializing Vertex AI: {e}")
        print("\nPlease ensure:")
        print("1. Vertex AI API is enabled in your project")
        print("2. Your credentials have proper permissions")
        print("3. gcloud CLI is installed and configured (optional)")
        return False

    # Test text moderation with Gemini
    print("\n" + "-" * 60)
    print("Testing Text Moderation with Gemini...")
    print("-" * 60)

    test_text = "This is a safe test message for content moderation."

    try:
        model = GenerativeModel("gemini-1.5-flash")

        prompt = f"""Analyze this text for inappropriate content: "{test_text}"

Respond with whether it's appropriate or not."""

        response = model.generate_content(
            prompt,
            safety_settings={
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
            }
        )

        print(f"✓ Text moderation successful!")
        print(f"  - Model: gemini-1.5-flash")

        # Show safety ratings
        if hasattr(response, 'candidates') and response.candidates:
            print("\n  Safety Ratings:")
            for rating in response.candidates[0].safety_ratings:
                category = rating.category.name.replace("HARM_CATEGORY_", "")
                probability = rating.probability.name
                print(f"    - {category}: {probability}")

        # Show response
        if hasattr(response, 'text'):
            print(f"\n  Response preview: {response.text[:200]}...")

    except Exception as e:
        print(f"❌ ERROR testing text moderation: {e}")
        return False

    # Test image moderation with Gemini
    print("\n" + "-" * 60)
    print("Testing Image Moderation with Gemini...")
    print("-" * 60)

    try:
        # Create a simple test image (1x1 white pixel PNG)
        import base64
        from PIL import Image
        import io

        # Create 1x1 white image
        img = Image.new('RGB', (1, 1), color='white')
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        img_bytes = img_byte_arr.getvalue()

        model = GenerativeModel("gemini-1.5-flash")

        image_part = Part.from_data(img_bytes, mime_type="image/png")

        prompt = "Analyze this image for any inappropriate content. Is it safe?"

        response = model.generate_content(
            [image_part, prompt],
            safety_settings={
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
            }
        )

        print(f"✓ Image moderation successful!")
        print(f"  - Model: gemini-1.5-flash")

        # Show safety ratings
        if hasattr(response, 'candidates') and response.candidates:
            print("\n  Safety Ratings:")
            for rating in response.candidates[0].safety_ratings:
                category = rating.category.name.replace("HARM_CATEGORY_", "")
                probability = rating.probability.name
                print(f"    - {category}: {probability}")

        # Show response
        if hasattr(response, 'text'):
            print(f"\n  Response preview: {response.text[:200]}...")

    except Exception as e:
        print(f"❌ ERROR testing image moderation: {e}")
        return False

    # Success!
    print("\n" + "=" * 60)
    print("✅ All tests passed! Your Vertex AI setup is working correctly.")
    print("=" * 60)
    print("\nYou can now run the FastAPI server:")
    print("  uvicorn src.main:app --reload")
    print()

    return True


if __name__ == "__main__":
    success = test_vertex_ai_connection()
    exit(0 if success else 1)
