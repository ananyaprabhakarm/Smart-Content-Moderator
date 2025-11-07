# Smart Content Moderator

A FastAPI-based content moderation service that analyzes text and images for inappropriate material and stores analysis summaries in a database.

## Features

- **Text Moderation API**: Analyze text content for inappropriate material
- **Image Moderation API**: Analyze uploaded images for inappropriate content
- **Analysis Summary API**: Retrieve moderation results by ID or list all results with filtering

## Database Schema

The service uses three main tables:

1. **moderation_requests**: Stores incoming moderation requests
   - id, content_type, content_hash, status, created_at

2. **moderation_results**: Stores analysis results
   - request_id, classification, confidence, reasoning, llm_response

3. **notification_logs**: Stores notification delivery logs
   - request_id, channel, status, sent_at

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd Baya-Task
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

## Running the Application

Start the development server:
```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API Endpoints

### 1. Text Moderation
**POST** `/api/text/moderate`

Analyze text content for inappropriate material.

Request body:
```json
{
  "text": "Your text content here",
  "content_id": "optional-identifier"
}
```

Response:
```json
{
  "request_id": 1,
  "status": "completed",
  "message": "Text moderation completed. Classification: appropriate"
}
```

### 2. Image Moderation
**POST** `/api/image/moderate`

Analyze uploaded images for inappropriate content.

Request (multipart/form-data):
- `image`: Image file (JPEG, PNG, GIF, WebP)
- `content_id`: Optional identifier (string)

Response:
```json
{
  "request_id": 2,
  "status": "completed",
  "message": "Image moderation completed. Classification: appropriate"
}
```

### 3. Get Analysis Summary (Single)
**GET** `/api/summary/{request_id}`

Retrieve analysis summary for a specific moderation request.

Response:
```json
{
  "request_id": 1,
  "content_type": "text",
  "content_hash": "abc123...",
  "status": "completed",
  "created_at": "2024-01-01T12:00:00Z",
  "result": {
    "classification": "appropriate",
    "confidence": 0.95,
    "reasoning": "No inappropriate content detected."
  }
}
```

### 4. Get Analysis Summaries (List)
**GET** `/api/summary`

Get a paginated list of analysis summaries with optional filtering.

Query parameters:
- `skip`: Number of records to skip (default: 0)
- `limit`: Number of records to return (default: 10, max: 100)
- `content_type`: Filter by content type (text/image)
- `status`: Filter by status (pending/completed/failed)

Response:
```json
{
  "total": 50,
  "summaries": [
    {
      "request_id": 1,
      "content_type": "text",
      "content_hash": "abc123...",
      "status": "completed",
      "created_at": "2024-01-01T12:00:00Z",
      "result": {
        "classification": "appropriate",
        "confidence": 0.95,
        "reasoning": "No inappropriate content detected."
      }
    }
  ]
}
```

## Project Structure

```
Baya-Task/
├── src/
│   ├── api/                    # API endpoints
│   │   ├── text_moderation.py
│   │   ├── image_moderation.py
│   │   └── summary.py
│   ├── database/               # Database configuration
│   │   └── connection.py
│   ├── models/                 # SQLAlchemy models
│   │   └── moderation.py
│   ├── schemas/                # Pydantic schemas
│   │   └── moderation.py
│   ├── services/               # Business logic
│   │   └── moderation_service.py
│   └── main.py                 # FastAPI application
├── .env.example                # Environment variables template
├── .gitignore
├── requirements.txt
└── README.md
```

## AI-Powered Moderation

### Image Moderation with CLIP
The image moderation service uses **OpenAI's CLIP** (Contrastive Language-Image Pre-training) model for zero-shot classification. CLIP compares images against text descriptions of inappropriate and appropriate content categories.

**Features:**
- Zero-shot classification (no training required)
- Analyzes images against 10+ inappropriate content categories
- Provides confidence scores and detailed reasoning
- Supports multiple image formats (JPEG, PNG, GIF, WebP)

**Content Categories Detected:**
- Violent content & graphic violence
- Explicit sexual content & nudity
- Hate symbols & offensive gestures
- Weapons, blood and gore
- Drug use & self-harm

### Text Moderation
The current text moderation uses basic keyword matching. You can enhance it with:
- OpenAI Moderation API
- Google Perspective API
- Azure Content Moderator
- Custom LLM (Claude, GPT-4, etc.)

### Extending Image Moderation
While CLIP provides powerful zero-shot classification, you can also integrate:
- AWS Rekognition (more comprehensive detection)
- Google Cloud Vision API
- Azure Computer Vision
- Custom trained models for specific use cases

Update the [src/services/moderation_service.py](src/services/moderation_service.py) file to customize categories or integrate additional services.

## License

MIT
