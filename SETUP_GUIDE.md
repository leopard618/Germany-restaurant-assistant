# Setup Guide

Complete setup instructions for the Restaurant Reservation Voice AI Agent.

## Step 1: Prerequisites

Install required software:
- Python 3.9 or higher
- ngrok (download from https://ngrok.com/)

## Step 2: Twilio Setup

### 2.1 Create Account
1. Visit https://www.twilio.com/try-twilio
2. Sign up for free account
3. Verify email and phone number

### 2.2 Get Phone Number
1. Go to **Phone Numbers** → **Manage** → **Buy a number**
2. Select **United States**
3. Check **Voice** capability
4. Purchase number

### 2.3 Get Credentials
1. Go to **Console Dashboard**
2. Copy:
   - Account SID (starts with AC...)
   - Auth Token (click to reveal)
3. Note your phone number

## Step 3: LiveKit Setup

### 3.1 Create Account
1. Visit https://cloud.livekit.io/
2. Sign up for free account
3. Create new project

### 3.2 Get Credentials
1. Go to **Settings** → **Keys**
2. Create new API Key/Secret pair
3. Copy:
   - API Key (starts with API...)
   - API Secret
   - WebSocket URL (wss://your-project.livekit.cloud)

## Step 4: OpenAI Setup

1. Visit https://platform.openai.com/
2. Create account or log in
3. Go to **API Keys**
4. Create new API key
5. Copy and save securely

## Step 5: Project Setup

### 5.1 Install Dependencies

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Mac/Linux)
source venv/bin/activate

# Install packages
pip install -r requirements.txt
```

### 5.2 Create .env File

Create `.env` in project root:

```env
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_PHONE_NUMBER=+1234567890
LIVEKIT_URL=wss://your-project.livekit.cloud
LIVEKIT_API_KEY=APIxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
LIVEKIT_API_SECRET=your_api_secret_here
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
LOG_LEVEL=INFO
WEBHOOK_PORT=8080
WEBHOOK_HOST=0.0.0.0
```

Replace all values with your actual credentials.

## Step 6: Start Services

### 6.1 Start Webhook Server

Terminal 1:
```bash
venv\Scripts\activate
python webhook.py
```

Server should start on port 8080.

### 6.2 Start ngrok

Terminal 2:
```bash
ngrok http 8080
```

Copy the HTTPS URL (e.g., `https://abc123.ngrok.io`)

### 6.3 Configure Twilio Webhook

1. Go to Twilio Console → **Phone Numbers** → **Active numbers**
2. Click your purchased number
3. Scroll to **Voice Configuration**
4. Under "A CALL COMES IN":
   - Select **Webhook**
   - Enter: `https://your-ngrok-url.ngrok.io/webhook/incoming`
   - Method: **HTTP POST**
5. Click **Save**

### 6.4 Start AI Agent

Terminal 3:
```bash
venv\Scripts\activate
python agent.py
```

Agent will connect to LiveKit and wait for calls.

## Step 7: Test

1. Call your Twilio phone number from any phone
2. You should hear the AI assistant greeting
3. Try making a restaurant reservation
4. Check terminal logs for activity

## Verification Checklist

- [ ] Webhook server running on port 8080
- [ ] ngrok tunnel active
- [ ] Twilio webhook configured correctly
- [ ] AI agent connected to LiveKit
- [ ] Test call successful
- [ ] AI responds to voice input

## Common Issues

**Port already in use:**
- Change `WEBHOOK_PORT` in `.env` to different port
- Update ngrok command: `ngrok http 8081`

**Webhook not receiving calls:**
- Verify ngrok URL is correct in Twilio
- Check webhook server logs
- Ensure ngrok is running

**Agent not connecting:**
- Verify LiveKit credentials in `.env`
- Check LiveKit dashboard for connection status
- Review agent logs for errors

**No audio:**
- Check Twilio call logs
- Verify webhook is receiving events
- Review media stream logs

## Next Steps

- Test with multiple concurrent calls
- Monitor performance metrics
- Customize system prompt in `config.py`
- Deploy to production environment

## Support

For issues:
1. Check logs in all terminals
2. Verify all credentials are correct
3. Review Twilio and LiveKit dashboards
4. Check API status pages

