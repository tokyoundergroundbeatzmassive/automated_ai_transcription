# Automated Meeting Transcriptor

An AWS Lambda function that automatically transcribes audio files stored in Dropbox and sends meeting summaries to Slack.

## Overview

1. Monitors a specific Dropbox folder (/automated_transcriptor)
2. When new audio files are added, transcribes them using Deepgram AI
3. Analyzes the transcribed text using OpenAI GPT
4. Sends meeting summaries to Slack

## Environment Variables

The following environment variables need to be set in the Lambda function:

```
DEEPGRAM_API_KEY=your_deepgram_api_key
DROPBOX_APP_KEY=your_dropbox_app_key
DROPBOX_APP_SECRET=your_dropbox_app_secret
DROPBOX_REFRESH_TOKEN=your_dropbox_refresh_token
OPENAI_API_KEY=your_openai_api_key
SLACK_WEBHOOK_URL=your_slack_webhook_url
```

### How to Obtain API Keys

1. Deepgram API Key
   - Create an account at [Deepgram Console](https://console.deepgram.com/signup)
   - Generate an API key

2. Dropbox API Credentials
   - Create an app in the [Dropbox Developer Console](https://www.dropbox.com/developers)
   - Obtain App Key and App Secret
   - Get Refresh Token through OAuth2.0 flow

3. OpenAI API Key
   - Generate an API key from the [OpenAI Dashboard](https://platform.openai.com/api-keys)

4. Slack Webhook URL
   - Create a new app in your Slack workspace
   - Enable Incoming Webhooks
   - Get the Webhook URL

## Supported Audio Formats

The following audio formats are supported:
- MP3 (.mp3)
- MP4 (.mp4)
- MP2 (.mp2)
- AAC (.aac)
- WAV (.wav)
- FLAC (.flac)
- PCM (.pcm)
- M4A (.m4a)
- OGG (.ogg)
- OPUS (.opus)
- WEBM (.webm)

## File Size Limit

- Maximum file size: 2GB

## Output Format

### Slack Notification Content

The notification includes:
1. List of participants
2. Detailed meeting summary
3. Action items
4. Updates to quotes or proposals
5. Pricing updates and key dates

## Development Setup

1. Clone the repository
```bash
git clone https://github.com/tokyoundergroundbeatzmassive/automated_ai_transcription.git
cd automated_ai_transcription
```

2. Create and activate virtual environment
```bash
python -m venv venv
source venv/bin/activate  # Unix-like systems
venv\Scripts\activate     # Windows
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Set up environment variables for local testing
```bash
# Create .env file
DEEPGRAM_API_KEY=your_deepgram_api_key
DROPBOX_APP_KEY=your_dropbox_app_key
DROPBOX_APP_SECRET=your_dropbox_app_secret
DROPBOX_REFRESH_TOKEN=your_dropbox_refresh_token
OPENAI_API_KEY=your_openai_api_key
SLACK_WEBHOOK_URL=your_slack_webhook_url
```

## Deployment

1. Create Lambda Layer
   ```bash
   # Create a directory for the layer
   mkdir -p python/lib/python3.11/site-packages
   
   # Install required packages
   pip install pydantic-core pydantic dropbox requests deepgram-sdk openai \
       --platform manylinux2014_x86_64 \
       -t python/lib/python3.11/site-packages \
       --only-binary=:all:
   
   # Create layer.zip
   zip -r layer.zip python
   ```

2. Set up Lambda Layer
   - Go to AWS Lambda console
   - Navigate to Layers
   - Create layer
   - Upload the created `layer.zip`
   - Select compatible runtime (Python 3.11 or later)

3. Create Lambda Function
   - Zip the function code
   ```bash
   zip -r function.zip automatedTranscriptor/
   ```
   - Create new Lambda function with Python 3.11 or later runtime
   - Upload function.zip
   - Add the layer to your function
   - Configure environment variables (see Environment Variables section)
   - Set up necessary IAM roles and policies (e.g., DynamoDB access)
   - Set memory to 1024 MB or higher
   - Set timeout to 5 minutes

4. Configure CORS Settings
   - Origins: https://www.dropbox.com, https://api.dropboxapi.com
   - Methods: GET, POST
   - Cache: 3600

5. Configure Dropbox Webhook
   - Set up your Dropbox app at https://www.dropbox.com/developers/apps
   - Use http://localhost for OAuth2 during development
   - Configure the webhook URL to point to your Lambda function

6. Configure Slack Integration
   - Create a Slack app at https://api.slack.com/apps
   - Specify the target channel
   - Configure the webhook URL

Note: The default target directory in Dropbox is `/automated_transcriptor`

## Important Notes

- Audio files are temporarily stored in the `/tmp` directory
- Ensure appropriate Lambda function timeout settings
- DynamoDB tables (DropboxTokens, DropboxCursors) are created automatically