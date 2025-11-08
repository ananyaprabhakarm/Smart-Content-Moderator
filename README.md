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

This service uses **OpenAI's omni-moderation-latest** model for both text and image content moderation. This is OpenAI's latest multimodal moderation model that provides state-of-the-art detection of inappropriate content.

### Features

**Unified Moderation API:**
- Single model for both text and images
- Real-time API-based analysis (no local model hosting required)
- Production-ready with high accuracy
- Detailed category-level scores and reasoning

**Content Categories Detected:**
The omni-moderation-latest model detects the following categories:
- **Sexual content**: Sexual descriptions or explicit material
- **Hate speech**: Content promoting hate based on identity
- **Harassment**: Bullying, threatening, or harassing content
- **Self-harm**: Content promoting self-harm or suicide
- **Sexual/minors**: Sexual content involving minors
- **Hate/threatening**: Hateful content with violence threats
- **Violence/graphic**: Graphic depictions of violence
- **Self-harm/intent**: Content showing intent to self-harm
- **Self-harm/instructions**: Instructions for self-harm
- **Harassment/threatening**: Harassing content with threats
- **Violence**: General violent content

**Image Analysis:**
- Supports JPEG, PNG, GIF, WebP formats
- Base64 encoding for secure transmission
- Analyzes visual content for all moderation categories
- Provides detailed scores per category

**Text Analysis:**
- Multi-language support
- Context-aware analysis
- Fine-grained category scoring
- Policy violation detection

### Setup

**Required: OpenAI API Key**

1. Get your API key from [OpenAI Platform](https://platform.openai.com/api-keys)
2. Copy `.env.example` to `.env`
3. Add your API key to the `.env` file:
```bash
OPENAI_API_KEY=your_actual_api_key_here
```

### Extending the Service

The current implementation uses OpenAI's omni-moderation-latest. You can extend or replace it with:
- **AWS Rekognition**: Enterprise-level content moderation
- **Google Cloud Vision API**: Image safety detection
- **Azure Content Moderator**: Microsoft's moderation service
- **Custom models**: Train your own models for specific use cases

Update [src/services/moderation_service.py](src/services/moderation_service.py) to integrate additional services or customize the moderation logic.

## License

MIT
