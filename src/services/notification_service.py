"""
Notification Service for Content Moderation Alerts

Sends notifications via:
- Slack (using Incoming Webhooks)
- Email (using Brevo API)
"""

import os
import json
from typing import Dict, Any
from datetime import datetime
import httpx


class NotificationService:
    """Service for sending notifications when inappropriate content is detected"""

    @staticmethod
    async def send_slack_notification(
        request_id: int,
        content_type: str,
        classification: str,
        confidence: float,
        reasoning: str,
        flagged_categories: list = None
    ) -> Dict[str, Any]:
        """
        Send notification to Slack webhook when inappropriate content is detected.

        Args:
            request_id: Moderation request ID
            content_type: Type of content (text/image)
            classification: appropriate/inappropriate
            confidence: Confidence score (0-1)
            reasoning: Explanation of the classification
            flagged_categories: List of flagged safety categories

        Returns:
            Dictionary with status and message
        """
        webhook_url = os.getenv("SLACK_WEBHOOK_URL")

        if not webhook_url:
            return {
                "status": "skipped",
                "message": "Slack webhook URL not configured"
            }

        try:
            # Determine color based on classification
            color = "danger" if classification == "inappropriate" else "good"

            # Build Slack message with blocks for better formatting
            blocks = [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": f"⚠️ Content Moderation Alert - {classification.upper()}",
                        "emoji": True
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"*Request ID:*\n{request_id}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Content Type:*\n{content_type}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Classification:*\n{classification}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Confidence:*\n{confidence:.2%}"
                        }
                    ]
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Reasoning:*\n{reasoning}"
                    }
                }
            ]

            # Add flagged categories if present
            if flagged_categories and len(flagged_categories) > 0:
                category_text = "\n• ".join(flagged_categories)
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Flagged Categories:*\n• {category_text}"
                    }
                })

            # Add timestamp footer
            blocks.append({
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"Detected at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                    }
                ]
            })

            # Prepare payload
            payload = {
                "attachments": [
                    {
                        "color": color,
                        "blocks": blocks
                    }
                ]
            }

            # Send to Slack webhook
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    webhook_url,
                    json=payload,
                    timeout=10.0
                )

                if response.status_code == 200:
                    return {
                        "status": "sent",
                        "message": "Slack notification sent successfully"
                    }
                else:
                    return {
                        "status": "failed",
                        "message": f"Slack API returned status {response.status_code}: {response.text}"
                    }

        except Exception as e:
            return {
                "status": "failed",
                "message": f"Error sending Slack notification: {str(e)}"
            }

    @staticmethod
    async def send_email_notification(
        request_id: int,
        content_type: str,
        classification: str,
        confidence: float,
        reasoning: str,
        flagged_categories: list = None
    ) -> Dict[str, Any]:
        """
        Send email notification via Brevo API when inappropriate content is detected.

        Args:
            request_id: Moderation request ID
            content_type: Type of content (text/image)
            classification: appropriate/inappropriate
            confidence: Confidence score (0-1)
            reasoning: Explanation of the classification
            flagged_categories: List of flagged safety categories

        Returns:
            Dictionary with status and message
        """
        brevo_api_key = os.getenv("BREVO_API_KEY")
        email_from_name = os.getenv("EMAIL_FROM_NAME", "Content Moderator")
        email_from = os.getenv("EMAIL_FROM")
        email_to = os.getenv("EMAIL_TO")
        email_to_name = os.getenv("EMAIL_TO_NAME", "Admin")

        # Check if Brevo is configured
        if not all([brevo_api_key, email_from, email_to]):
            return {
                "status": "skipped",
                "message": "Brevo email configuration not complete"
            }

        try:
            # Build plain text email body
            text_content = f"""
Content Moderation Alert
========================

Request ID: {request_id}
Content Type: {content_type}
Classification: {classification.upper()}
Confidence: {confidence:.2%}

Reasoning:
{reasoning}
"""

            if flagged_categories and len(flagged_categories) > 0:
                text_content += f"\nFlagged Categories:\n"
                for category in flagged_categories:
                    text_content += f"  • {category}\n"

            text_content += f"\nDetected at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            text_content += f"\n---\nSmart Content Moderator - Powered by Google Gemini AI\n"

            # Build HTML email body for better formatting
            html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
        }}
        .header {{
            background-color: #dc3545;
            color: white;
            padding: 20px;
            text-align: center;
            border-radius: 5px 5px 0 0;
        }}
        .content {{
            padding: 20px;
            background-color: #f8f9fa;
        }}
        .info-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            background-color: white;
        }}
        .info-table td {{
            padding: 12px;
            border-bottom: 1px solid #dee2e6;
        }}
        .label {{
            font-weight: bold;
            width: 150px;
            color: #495057;
        }}
        .reasoning {{
            background-color: white;
            padding: 15px;
            margin: 15px 0;
            border-left: 4px solid #dc3545;
        }}
        .categories {{
            background-color: white;
            padding: 15px;
            margin: 15px 0;
        }}
        .categories ul {{
            margin: 5px 0;
            padding-left: 20px;
        }}
        .footer {{
            color: #6c757d;
            font-size: 12px;
            margin-top: 20px;
            padding-top: 20px;
            border-top: 1px solid #dee2e6;
            text-align: center;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h2 style="margin: 0;">⚠️ Content Moderation Alert</h2>
        <h3 style="margin: 10px 0 0 0;">{classification.upper()}</h3>
    </div>
    <div class="content">
        <table class="info-table">
            <tr>
                <td class="label">Request ID:</td>
                <td><strong>{request_id}</strong></td>
            </tr>
            <tr>
                <td class="label">Content Type:</td>
                <td>{content_type.capitalize()}</td>
            </tr>
            <tr>
                <td class="label">Classification:</td>
                <td><strong style="color: #dc3545;">{classification.upper()}</strong></td>
            </tr>
            <tr>
                <td class="label">Confidence:</td>
                <td>{confidence:.2%}</td>
            </tr>
        </table>

        <div class="reasoning">
            <h3 style="margin-top: 0; color: #dc3545;">Reasoning:</h3>
            <p style="margin: 0;">{reasoning}</p>
        </div>
"""

            # Add flagged categories if present
            if flagged_categories and len(flagged_categories) > 0:
                html_content += """
        <div class="categories">
            <h3 style="margin-top: 0; color: #dc3545;">Flagged Categories:</h3>
            <ul>
"""
                for category in flagged_categories:
                    html_content += f"                <li>{category.replace('_', ' ').title()}</li>\n"
                html_content += """
            </ul>
        </div>
"""

            html_content += f"""
        <div class="footer">
            <p><strong>Detected at:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>Smart Content Moderator - Powered by Google Gemini AI</p>
        </div>
    </div>
</body>
</html>
"""

            # Prepare Brevo API request payload
            payload = {
                "sender": {
                    "name": email_from_name,
                    "email": email_from
                },
                "to": [
                    {
                        "email": email_to,
                        "name": email_to_name
                    }
                ],
                "subject": f"⚠️ Content Moderation Alert - {classification.upper()} (Request #{request_id})",
                "textContent": text_content,
                "htmlContent": html_content
            }

            # Send via Brevo API
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.brevo.com/v3/smtp/email",
                    headers={
                        "accept": "application/json",
                        "api-key": brevo_api_key,
                        "content-type": "application/json"
                    },
                    json=payload,
                    timeout=10.0
                )

                if response.status_code in [200, 201]:
                    return {
                        "status": "sent",
                        "message": "Email notification sent successfully via Brevo"
                    }
                else:
                    return {
                        "status": "failed",
                        "message": f"Brevo API returned status {response.status_code}: {response.text}"
                    }

        except Exception as e:
            return {
                "status": "failed",
                "message": f"Error sending Brevo email notification: {str(e)}"
            }

    @staticmethod
    async def notify_inappropriate_content(
        request_id: int,
        content_type: str,
        classification: str,
        confidence: float,
        reasoning: str,
        flagged_categories: list = None
    ) -> Dict[str, Dict[str, Any]]:
        """
        Send notifications via all configured channels (Slack + Email).

        Args:
            request_id: Moderation request ID
            content_type: Type of content (text/image)
            classification: appropriate/inappropriate
            confidence: Confidence score (0-1)
            reasoning: Explanation of the classification
            flagged_categories: List of flagged safety categories

        Returns:
            Dictionary with results from each channel
        """
        results = {
            "slack": None,
            "email": None
        }

        # Send Slack notification
        results["slack"] = await NotificationService.send_slack_notification(
            request_id=request_id,
            content_type=content_type,
            classification=classification,
            confidence=confidence,
            reasoning=reasoning,
            flagged_categories=flagged_categories
        )

        # Send Email notification
        results["email"] = await NotificationService.send_email_notification(
            request_id=request_id,
            content_type=content_type,
            classification=classification,
            confidence=confidence,
            reasoning=reasoning,
            flagged_categories=flagged_categories
        )

        return results
