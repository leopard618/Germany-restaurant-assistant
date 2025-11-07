# Restaurant Reservation Voice AI Agent

Voice AI assistant for restaurant reservations in Germany. Built with LiveKit, Twilio, and OpenAI Realtime API.

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
- Voice model (alloy, ash, ballad, coral, echo, sage, shimmer, verse, marin, cedar)
- System prompt
- Log level
- Concurrent call limits

## Deployment

### Option 1: LiveKit Cloud (Requires Docker) ⚡

**Best option for low latency!** Deploy your agent directly to LiveKit Cloud.

**Note:** LiveKit Cloud requires Docker. If you prefer not to use Docker, see Option 2 below.

See [LIVEKIT_CLOUD_DEPLOYMENT.md](LIVEKIT_CLOUD_DEPLOYMENT.md) for detailed instructions.

**Quick Start:**
```bash
# Install LiveKit CLI
npm install -g livekit-cli

# Authenticate
lk cloud auth

# Deploy agent (requires Dockerfile)
lk agent deploy
```

**Benefits:**
- ✅ Lowest latency (agents run on LiveKit infrastructure)
- ✅ Geographic affinity (agents placed close to users)
- ✅ Auto-scaling
- ✅ Managed infrastructure
- ⚠️ Requires Docker

### Option 2: Deploy Without Docker (Recommended for Simplicity) 🚀

**No Docker required!** Deploy directly to platforms that support Python.

**Best Options:**
- **Render.com** - Easy deployment, free tier available
- **Railway.app** - Simple UI, good developer experience
- **Fly.io** - Global distribution, low latency
- **Heroku** - Traditional PaaS, well-documented
- **DigitalOcean App Platform** - Good pricing
- **AWS/GCP/Azure** - Full control, custom infrastructure

See [DEPLOYMENT_NO_DOCKER.md](DEPLOYMENT_NO_DOCKER.md) for detailed instructions on all platforms.

**Quick Start (Render.com):**
1. Push code to GitHub
2. Go to https://render.com
3. Create Web Service → Connect GitHub → `python webhook.py`
4. Create Background Worker → Same repo → `python agent.py`
5. Add environment variables
6. Deploy!

**Benefits:**
- ✅ No Docker knowledge required
- ✅ Direct Python deployment
- ✅ Easy to set up
- ✅ Free tiers available

## License

MIT License
