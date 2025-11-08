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

This service uses **Google Gemini API** for both text and image content moderation. Gemini is Google's latest multimodal AI that provides powerful content safety analysis with built-in safety ratings - and it's **FREE** to use!

### Features

**Gemini API Moderation:**
- **100% FREE Tier**: 60 requests/min, 1,500 requests/day - No credit card required!
- **Multimodal Analysis**: Single model (Gemini Flash Latest) handles both text and images
- **Built-in Safety Ratings**: Automatic safety assessments across multiple harm categories
- **Super Simple Setup**: Just need an API key (no Google Cloud project required)
- **No Local Hosting**: Cloud-based API (no GPU or model hosting required)
- **Detailed Reasoning**: AI-generated explanations for moderation decisions

**Safety Categories Detected:**
Gemini's safety filters detect the following harm categories:
- **Hate Speech**: Content promoting hate or discrimination based on identity
- **Harassment**: Bullying, intimidating, or threatening behavior
- **Dangerous Content**: Content promoting harmful or dangerous activities
- **Sexually Explicit**: Adult or sexually suggestive material

**Probability Levels:**
- NEGLIGIBLE (0.1): Very unlikely to be harmful
- LOW (0.3): Low probability of harm
- MEDIUM (0.6): Moderate probability of harm - flagged
- HIGH (0.9): High probability of harm - flagged

**Image Analysis:**
- Supports JPEG, PNG, GIF, WebP formats
- Multimodal understanding (visual + text context)
- Analyzes visual content for all safety categories
- Provides probability scores per category

**Text Analysis:**
- Multi-language support (100+ languages)
- Context-aware safety assessment
- Fine-grained probability scoring
- AI-powered reasoning and explanations

### Setup (Super Simple!)

#### 1. Get Your FREE Gemini API Key

1. Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the API key

**That's it! No credit card, no complex setup required!**

#### 2. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env file and add your API key
```

Add to `.env`:
```bash
GOOGLE_API_KEY=your-actual-api-key-here
```

#### 3. Test Connection

```bash
# Run the test script
python test_gemini_api.py
```

If you see ✅ success messages, you're ready to go!

### Free Tier Limits

**Gemini API Free Tier (Generous!):**
- **60 requests per minute**
- **1,500 requests per day**
- **No credit card required**
- **No expiration** - free forever for this tier

Perfect for:
- Development and testing
- Small to medium websites
- Personal projects
- Proof of concepts

### Extending the Service

The current implementation uses Gemini API. You can extend or replace it with:
- **Google Vertex AI**: Enterprise version with higher limits (requires Google Cloud)
- **OpenAI Moderation API**: Alternative AI-based moderation
- **AWS Rekognition**: Enterprise-level content moderation
- **Azure Content Moderator**: Microsoft's moderation service
- **Custom models**: Train your own models

Update [src/services/moderation_service.py](src/services/moderation_service.py) to integrate additional services or customize the moderation logic.

## License

MIT
