import os
import requests
import json

SLACK_WEBHOOK_URL: str = os.environ.get('SLACK_WEBHOOK_URL', '')

if not SLACK_WEBHOOK_URL:
    raise ValueError("SLACK_WEBHOOK_URL environment variable is not set")

def send_slack_notification(meeting_summary, first_audio_file):
    slack_message = {
        "text": f"Meeting Summary has been generated from: {first_audio_file}",
        "attachments": [
            {
                "fields": [
                    {"title": "List of attendees", "value": meeting_summary["List of attendees"]},
                    {"title": "Meeting Summary", "value": meeting_summary["Meeting Summary"]},
                    {"title": "Action Items", "value": meeting_summary["Action Items"]},
                    {"title": "Quote/Proposal Updates", "value": meeting_summary["Quote/Proposal Updates"]},
                    {"title": "Pricing Updates/Key Dates", "value": meeting_summary["Pricing Updates/Key Dates"]},
                ]
            }
        ]
    }

    try:
        response = requests.post(SLACK_WEBHOOK_URL, data=json.dumps(slack_message), headers={'Content-Type': 'application/json'})
        response.raise_for_status()
        print("Slack notification sent successfully")
    except requests.exceptions.RequestException as e:
        print(f"Failed to send Slack notification: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"Response status code: {e.response.status_code}")
            print(f"Response text: {e.response.text}")
    except Exception as e:
        print(f"An unexpected error occurred while sending Slack notification: {e}")