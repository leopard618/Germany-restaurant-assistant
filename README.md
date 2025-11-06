# Restaurant Reservation Voice AI Agent

Voice AI assistant for restaurant reservations in Germany. Built with LiveKit, Twilio, and OpenAI Realtime API.

## Features

- Real-time voice conversations
- Low latency (<1s response time)
- Supports 100+ concurrent calls
- Restaurant booking management
- Multi-city support (Berlin, Munich, Hamburg, Frankfurt, Cologne, Stuttgart, Düsseldorf, Dresden)

## Architecture

```
Phone Call → Twilio → WebSocket → LiveKit → OpenAI Realtime API → Response
```

## Prerequisites

- Python 3.9+
- Twilio account with phone number
- LiveKit Cloud account
- OpenAI API key
- ngrok (for local development)

## Quick Start

### 1. Install Dependencies

```bash
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### 2. Configure Environment

Create `.env` file:

```env
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=your_phone_number
LIVEKIT_URL=wss://your-project.livekit.cloud
LIVEKIT_API_KEY=your_api_key
LIVEKIT_API_SECRET=your_api_secret
OPENAI_API_KEY=your_openai_key
```

### 3. Start Services

Terminal 1 - Webhook Server:
```bash
python webhook.py
```

Terminal 2 - AI Agent:
```bash
python agent.py
```

Terminal 3 - ngrok (for local testing):
```bash
ngrok http 8080
```

### 4. Configure Twilio

1. Go to Twilio Console → Phone Numbers → Active numbers
2. Click your number
3. Set Voice webhook: `https://your-ngrok-url.ngrok.io/webhook/incoming`
4. Method: POST

### 5. Test

Call your Twilio phone number to test the system.

## Project Structure

```
├── agent.py          # AI agent worker
├── webhook.py        # Twilio webhook handler
├── config.py         # Configuration
├── requirements.txt  # Dependencies
└── README.md         # This file
```

## Configuration

Edit `config.py` to customize:
- Voice model (alloy, echo, fable, onyx, nova, shimmer)
- System prompt
- Log level
- Concurrent call limits

## Production Deployment

1. Deploy to cloud (AWS/GCP/Azure)
2. Use proper domain with SSL
3. Update Twilio webhook URL
4. Set up monitoring and logging
5. Configure auto-scaling

## Troubleshooting

**Calls not connecting:**
- Verify webhook URL in Twilio
- Check webhook server is running
- Ensure ngrok is active (local dev)

**High latency:**
- Use LiveKit region closest to users
- Check internet connection
- Verify OpenAI API status

**Agent not responding:**
- Check API keys are valid
- Review logs for errors
- Verify LiveKit credentials

## License

MIT License
