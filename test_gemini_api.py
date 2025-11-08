#!/usr/bin/env python3
"""
Test script to verify Google Gemini API connection.
Run this script to check if your API key is working correctly.

Usage:
    python test_gemini_api.py
"""

import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

def test_gemini_connection():
    """Test Gemini API connection"""

    print("=" * 60)
    print("Google Gemini API Connection Test")
    print("=" * 60)

    # Check if API key exists
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("❌ ERROR: GOOGLE_API_KEY not found in environment variables")
        print("\nPlease:")
        print("1. Go to https://aistudio.google.com/app/apikey")
        print("2. Create a new API key (it's FREE!)")
        print("3. Copy .env.example to .env")
        print("4. Add your API key to the .env file")
        return False

    print(f"✓ API Key found: {api_key[:8]}...{api_key[-4:]}")

    # Initialize Gemini
    try:
        genai.configure(api_key=api_key)
        print("✓ Gemini API configured")
    except Exception as e:
        print(f"❌ ERROR configuring Gemini: {e}")
        return False

    # Test text generation/moderation
    print("\n" + "-" * 60)
    print("Testing Text Moderation...")
    print("-" * 60)

    test_text = "This is a safe test message for content moderation."

    try:
        model = genai.GenerativeModel("gemini-flash-latest")

        # Set safety settings to get ratings
        safety_settings = [
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
        ]

        response = model.generate_content(
            f"Analyze this text for safety: '{test_text}'",
            safety_settings=safety_settings
        )

        print(f"✓ Text moderation successful!")
        print(f"  - Model: gemini-flash-latest")

        # Show safety ratings
        if hasattr(response, 'candidates') and response.candidates:
            print("\n  Safety Ratings:")
            for rating in response.candidates[0].safety_ratings:
                category = rating.category.name.replace("HARM_CATEGORY_", "")
                probability = rating.probability.name
                print(f"    - {category}: {probability}")

        # Show response preview
        if hasattr(response, 'text') and response.text:
            print(f"\n  Response preview: {response.text[:150]}...")

    except Exception as e:
        print(f"❌ ERROR testing text moderation: {e}")
        return False

    # Test image moderation
    print("\n" + "-" * 60)
    print("Testing Image Moderation...")
    print("-" * 60)

    try:
        from PIL import Image
        import io

        # Create a simple test image (100x100 white square)
        img = Image.new('RGB', (100, 100), color='white')
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        img_bytes = img_byte_arr.getvalue()

        model = genai.GenerativeModel("gemini-flash-latest")

        # Upload image
        uploaded_file = genai.upload_file(io.BytesIO(img_bytes), mime_type="image/png")

        response = model.generate_content(
            [uploaded_file, "Analyze this image for any inappropriate content."],
            safety_settings=safety_settings
        )

        print(f"✓ Image moderation successful!")
        print(f"  - Model: gemini-flash-latest")

        # Show safety ratings
        if hasattr(response, 'candidates') and response.candidates:
            print("\n  Safety Ratings:")
            for rating in response.candidates[0].safety_ratings:
                category = rating.category.name.replace("HARM_CATEGORY_", "")
                probability = rating.probability.name
                print(f"    - {category}: {probability}")

        # Show response preview
        if hasattr(response, 'text') and response.text:
            print(f"\n  Response preview: {response.text[:150]}...")

        # Clean up uploaded file
        try:
            genai.delete_file(uploaded_file.name)
            print("  - Temporary file cleaned up")
        except:
            pass

    except Exception as e:
        print(f"❌ ERROR testing image moderation: {e}")
        return False

    # Success!
    print("\n" + "=" * 60)
    print("✅ All tests passed! Your Gemini API is working correctly.")
    print("=" * 60)
    print("\nFree Tier Information:")
    print("  - 60 requests per minute")
    print("  - 1,500 requests per day")
    print("  - No credit card required!")
    print("\nYou can now run the FastAPI server:")
    print("  uvicorn src.main:app --reload")
    print()

    return True


if __name__ == "__main__":
    success = test_gemini_connection()
    exit(0 if success else 1)
