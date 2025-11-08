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

This service uses **Google Vertex AI with Gemini models** for both text and image content moderation. Gemini is Google's latest multimodal AI that provides powerful content safety analysis with built-in safety ratings.

### Features

**Vertex AI Gemini Moderation:**
- **Multimodal Analysis**: Single model (Gemini 1.5 Flash) handles both text and images
- **Built-in Safety Ratings**: Automatic safety assessments across multiple harm categories
- **No Local Hosting**: Cloud-based API (no GPU or model hosting required)
- **Production-Ready**: Enterprise-grade reliability with Google Cloud infrastructure
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

### Setup

**Required: Google Cloud Project with Vertex AI**

#### 1. Create Google Cloud Project

```bash
# Install Google Cloud CLI (if not already installed)
# Visit: https://cloud.google.com/sdk/docs/install

# Create a new project (or use existing)
gcloud projects create your-project-id
gcloud config set project your-project-id

# Enable Vertex AI API
gcloud services enable aiplatform.googleapis.com
```

#### 2. Set Up Authentication

**Option A: Service Account (Recommended for production)**
```bash
# Create service account
gcloud iam service-accounts create content-moderator \
    --display-name="Content Moderation Service"

# Grant necessary permissions
gcloud projects add-iam-policy-binding your-project-id \
    --member="serviceAccount:content-moderator@your-project-id.iam.gserviceaccount.com" \
    --role="roles/aiplatform.user"

# Create and download key
gcloud iam service-accounts keys create ~/service-account-key.json \
    --iam-account=content-moderator@your-project-id.iam.gserviceaccount.com
```

**Option B: Application Default Credentials (Development)**
```bash
gcloud auth application-default login
```

#### 3. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your configuration
```

Add to `.env`:
```bash
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_LOCATION=us-central1
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json  # If using service account
```

#### 4. Test Connection

```bash
# Run the test script
python test_vertexai_api.py
```

### Cost Considerations

Vertex AI Gemini pricing (as of 2024):
- **Gemini 1.5 Flash**: $0.00001875 per 1K characters (input)
- Very affordable for content moderation use cases
- First 1000 requests per month are free

### Extending the Service

The current implementation uses Vertex AI Gemini. You can extend or replace it with:
- **AWS Rekognition**: Enterprise-level content moderation
- **Azure Content Moderator**: Microsoft's moderation service
- **OpenAI Moderation API**: Alternative AI-based moderation
- **Custom models**: Deploy your own models on Vertex AI

Update [src/services/moderation_service.py](src/services/moderation_service.py) to integrate additional services or customize the moderation logic.

## License

MIT
