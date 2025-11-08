# Analytics Endpoint Usage Guide

## Overview
The analytics endpoint provides aggregated moderation data for specific users, allowing you to track usage patterns, content types, and moderation results.

## Endpoint Details

### GET `/api/v1/analytics/summary`

Retrieve analytics summary for a specific user.

**Query Parameters:**
- `user` (required): User's email address

**Example Request:**
```bash
curl "http://localhost:8000/api/v1/analytics/summary?user=abcxyz@gmail.com"
```

**Example Response:**
```json
{
  "user_email": "abcxyz@gmail.com",
  "total_requests": 25,
  "content_type_breakdown": {
    "text": 18,
    "image": 7
  },
  "classification_breakdown": {
    "appropriate": 21,
    "inappropriate": 4
  },
  "status_breakdown": {
    "pending": 1,
    "completed": 23,
    "failed": 1
  },
  "average_confidence": 0.87,
  "first_request_date": "2024-01-15T10:30:00Z",
  "last_request_date": "2024-01-20T15:45:00Z"
}
```

## Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `user_email` | string | Email address of the user |
| `total_requests` | integer | Total number of moderation requests submitted |
| `content_type_breakdown` | object | Count of requests by content type (text/image) |
| `classification_breakdown` | object | Count of results by classification (appropriate/inappropriate) |
| `status_breakdown` | object | Count of requests by status (pending/completed/failed) |
| `average_confidence` | float \| null | Average confidence score across all completed moderations |
| `first_request_date` | datetime \| null | Timestamp of the user's first moderation request |
| `last_request_date` | datetime \| null | Timestamp of the user's most recent moderation request |

## Error Responses

### 404 - User Not Found
```json
{
  "detail": "No moderation requests found for user: unknown@example.com"
}
```

### 422 - Missing Query Parameter
```json
{
  "detail": [
    {
      "type": "missing",
      "loc": ["query", "user"],
      "msg": "Field required"
    }
  ]
}
```

## Integration with Moderation Endpoints

To enable analytics tracking, include the `user_email` field when submitting content for moderation:

### Text Moderation
```bash
curl -X POST "http://localhost:8000/api/text/moderate" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Your content here",
    "user_email": "abcxyz@gmail.com"
  }'
```

### Image Moderation
```bash
curl -X POST "http://localhost:8000/api/image/moderate" \
  -F "image=@/path/to/image.jpg" \
  -F "user_email=abcxyz@gmail.com"
```

## Database Changes

The analytics endpoint requires a new `user_email` column in the `moderation_requests` table:

### Migration
If you have an existing database, run the migration script:
```bash
python migrate_add_user_email.py
```

### Fresh Installation
For new installations, the column will be created automatically when the application starts.

## API Documentation

Once the server is running, visit these URLs for interactive documentation:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Example Use Cases

### 1. User Dashboard
Display personal moderation statistics to users showing their content submission history and approval rates.

### 2. Admin Monitoring
Track power users or identify users who frequently submit inappropriate content.

### 3. Usage Analytics
Analyze which users rely more on text vs. image moderation.

### 4. Compliance Reporting
Generate reports showing moderation activity for specific users over time.

## Notes

- The `user_email` field is **optional** on moderation endpoints for backward compatibility
- Requests without a `user_email` will still be processed but won't appear in analytics
- The analytics endpoint requires at least one moderation request for the specified user
