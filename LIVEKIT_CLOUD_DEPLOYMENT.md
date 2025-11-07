# LiveKit Cloud Deployment Guide

**Best option for low latency!** Deploy your agent directly to LiveKit Cloud for optimal performance.

## Why LiveKit Cloud?

✅ **Lowest Latency** - Agents run on LiveKit infrastructure, minimizing network hops  
✅ **Geographic Affinity** - Agents automatically placed close to users  
✅ **Auto-Scaling** - Automatically scales based on demand  
✅ **Stateful Load Balancing** - Sessions stay on same server for consistency  
✅ **Managed Infrastructure** - No server management needed  

## Prerequisites

1. **LiveKit Cloud Account** - Sign up at https://cloud.livekit.io
2. **LiveKit CLI** - Install the LiveKit CLI tool
3. **Dockerfile** - Required for LiveKit Cloud deployment (see below)
4. **GitHub Repository** (recommended for CI/CD)

**Note:** LiveKit Cloud requires Docker. If you prefer not to use Docker, see [DEPLOYMENT_NO_DOCKER.md](DEPLOYMENT_NO_DOCKER.md) for alternative deployment options.

## Installation

### 1. Install LiveKit CLI

**Windows (PowerShell):**
```powershell
# Using Scoop
scoop install livekit-cli

# Or download from: https://github.com/livekit/livekit-cli/releases
```

**macOS/Linux:**
```bash
# Using Homebrew
brew install livekit-cli

# Or using npm
npm install -g livekit-cli
```

### 2. Authenticate with LiveKit Cloud

```bash
lk cloud auth
```

This will open your browser to authenticate. You'll need:
- Your LiveKit Cloud account
- API credentials from your LiveKit Cloud project

## Deployment Methods

### Method 1: Using LiveKit CLI (Recommended)

#### Step 1: Prepare Your Code

Ensure your repository has:
- `agent.py` - Your agent code
- `config.py` - Configuration file
- `requirements.txt` - Python dependencies
- `Dockerfile` - Container definition (required - see below to create one)

**Create Dockerfile:**

Create a `Dockerfile` in your project root:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY agent.py .
COPY config.py .

# Set environment variables (can be overridden in LiveKit Cloud dashboard)
ENV PYTHONUNBUFFERED=1

# Run the agent
CMD ["python", "agent.py"]
```

#### Step 2: Set Environment Variables

You can set environment variables in two ways:

**Option A: In LiveKit Cloud Dashboard (Recommended)**
1. Go to LiveKit Cloud Dashboard
2. Navigate to **Agents** section
3. Click on your agent
4. Go to **Environment Variables**
5. Add:
   ```
   LIVEKIT_URL=wss://your-project.livekit.cloud
   LIVEKIT_API_KEY=your_api_key
   LIVEKIT_API_SECRET=your_api_secret
   OPENAI_API_KEY=your_openai_key
   LOG_LEVEL=INFO
   VOICE_MODEL=shimmer
   ```

**Option B: Using CLI**
```bash
lk agent update <agent-name> \
  --env LIVEKIT_URL=wss://your-project.livekit.cloud \
  --env LIVEKIT_API_KEY=your_api_key \
  --env LIVEKIT_API_SECRET=your_api_secret \
  --env OPENAI_API_KEY=your_openai_key \
  --env LOG_LEVEL=INFO \
  --env VOICE_MODEL=shimmer
```

#### Step 3: Deploy Agent

**From Local Directory:**
```bash
# Navigate to your project directory
cd E:\Workspace\AI\Gemany-restaurant-assistant

# Deploy the agent
lk agent deploy
```

**From GitHub Repository:**
```bash
lk agent deploy --repo https://github.com/yourusername/your-repo
```

The CLI will:
1. Build a Docker image from your `Dockerfile`
2. Push it to LiveKit Cloud's container registry
3. Deploy the agent to your LiveKit Cloud project
4. Start the agent worker

### Method 2: Using LiveKit Cloud Dashboard

#### Step 1: Go to Agents Section

1. Log in to LiveKit Cloud Dashboard
2. Select your project
3. Navigate to **Agents** in the sidebar

#### Step 2: Create New Agent

1. Click **"Create Agent"** or **"New Agent"**
2. Fill in the form:
   - **Name**: `restaurant-assistant-agent`
   - **Source**: Choose one:
     - **GitHub Repository**: Connect your GitHub repo
     - **Docker Image**: Use a pre-built image
     - **Upload**: Upload your code directly

#### Step 3: Configure Agent

**If using GitHub:**
- **Repository**: `yourusername/your-repo`
- **Branch**: `main` (or your branch)
- **Dockerfile Path**: `Dockerfile` (or leave default)
- **Entrypoint**: Leave default (uses `agent.py`)

**If using Docker Image:**
- **Image URL**: `your-registry/your-image:tag`

#### Step 4: Set Environment Variables

In the agent configuration, add environment variables:

```
LIVEKIT_URL=wss://your-project.livekit.cloud
LIVEKIT_API_KEY=your_api_key
LIVEKIT_API_SECRET=your_api_secret
OPENAI_API_KEY=your_openai_key
LOG_LEVEL=INFO
VOICE_MODEL=shimmer
```

**Important:** Even though the agent connects to LiveKit, you still need to provide credentials because:
- The agent needs to authenticate to join rooms
- Different agents can connect to different LiveKit projects

#### Step 5: Deploy

1. Click **"Deploy"** or **"Save"**
2. Wait for the build to complete (usually 2-5 minutes)
3. Check the **Logs** tab to verify the agent started successfully

## Architecture

When deployed to LiveKit Cloud:

```
Phone Call → Twilio → Webhook Server (Render/Cloud) → LiveKit Room
                                                              ↓
                                                    Agent (LiveKit Cloud)
                                                              ↓
                                                    OpenAI Realtime API
```

**Key Benefits:**
- Agent runs on LiveKit infrastructure (lowest latency)
- Webhook server can be anywhere (just needs to create rooms)
- Automatic geographic distribution

## Configuration

### Environment Variables

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `LIVEKIT_URL` | Yes | Your LiveKit Cloud WebSocket URL | `wss://your-project.livekit.cloud` |
| `LIVEKIT_API_KEY` | Yes | LiveKit API Key | `APxxxxxxxxxxxxx` |
| `LIVEKIT_API_SECRET` | Yes | LiveKit API Secret | `xxxxxxxxxxxxx` |
| `OPENAI_API_KEY` | Yes | OpenAI API Key | `sk-xxxxxxxxxxxxx` |
| `VOICE_MODEL` | No | Voice model (default: shimmer) | `shimmer`, `sage`, `coral`, etc. |
| `LOG_LEVEL` | No | Logging level (default: INFO) | `INFO`, `DEBUG`, `WARNING` |

### Scaling Configuration

In LiveKit Cloud Dashboard:
- **Min Instances**: 0 (scales to zero when idle)
- **Max Instances**: 10+ (adjust based on expected load)
- **Auto-scaling**: Enabled by default

## Monitoring

### View Agent Status

1. Go to LiveKit Cloud Dashboard → **Agents**
2. Click on your agent
3. View:
   - **Status**: Running/Stopped/Error
   - **Active Sessions**: Current number of active calls
   - **Logs**: Real-time logs
   - **Metrics**: CPU, Memory, Latency

### View Logs

**In Dashboard:**
- Navigate to your agent → **Logs** tab
- Real-time streaming logs
- Filter by level (INFO, ERROR, etc.)

**Using CLI:**
```bash
lk agent logs <agent-name>
```

### Metrics

LiveKit Cloud provides:
- **Active Sessions**: Number of concurrent calls
- **Latency**: P50, P95, P99 latencies
- **Error Rate**: Failed sessions percentage
- **CPU/Memory**: Resource usage

## Updating Your Agent

### Method 1: Auto-Deploy from GitHub

1. Push changes to your repository
2. LiveKit Cloud will automatically rebuild and redeploy
3. Zero-downtime deployment (new instances start before old ones stop)

### Method 2: Manual Update via CLI

```bash
# Rebuild and redeploy
lk agent deploy

# Or update specific settings
lk agent update <agent-name> --env NEW_VAR=value
```

### Method 3: Manual Update via Dashboard

1. Go to agent settings
2. Click **"Redeploy"** or **"Update"**
3. Or update environment variables and save

## Troubleshooting

### Agent Not Starting

**Check Logs:**
```bash
lk agent logs <agent-name>
```

**Common Issues:**
1. **Missing Environment Variables**
   - Verify all required env vars are set
   - Check for typos in variable names

2. **Invalid API Keys**
   - Verify LiveKit credentials are correct
   - Check OpenAI API key is valid

3. **Build Errors**
   - Check Dockerfile syntax
   - Verify all dependencies in requirements.txt

### High Latency

1. **Check Agent Region**
   - Ensure agent is deployed in region closest to users
   - LiveKit Cloud auto-selects, but you can specify

2. **Check OpenAI Region**
   - OpenAI Realtime API latency affects overall latency
   - Consider using OpenAI regions closer to your users

3. **Monitor Metrics**
   - Check P95/P99 latencies in dashboard
   - Look for network issues

### Agent Not Handling Calls

1. **Verify Webhook Server**
   - Ensure webhook server is running
   - Check webhook URL in Twilio

2. **Check Room Creation**
   - Verify webhook creates rooms correctly
   - Check LiveKit credentials in webhook server

3. **Check Agent Logs**
   - Look for connection errors
   - Verify agent can connect to LiveKit

## Best Practices for Low Latency

1. **Deploy Agent to LiveKit Cloud** ✅ (You're doing this!)
2. **Use Same Region** - Deploy webhook server in same region as LiveKit Cloud
3. **Optimize Turn Detection** - Adjust VAD settings in `agent.py`
4. **Monitor Metrics** - Watch latency metrics and optimize
5. **Use CDN** - If serving static assets, use CDN
6. **Connection Pooling** - LiveKit handles this automatically

## Cost Considerations

LiveKit Cloud pricing:
- **Pay per use** - Only pay for active agent time
- **Scales to zero** - No cost when idle
- **Transparent pricing** - Check LiveKit Cloud pricing page

Typical costs:
- Small scale (< 100 calls/day): ~$10-50/month
- Medium scale (100-1000 calls/day): ~$50-200/month
- Large scale (1000+ calls/day): Custom pricing

## Next Steps

1. ✅ Deploy agent to LiveKit Cloud
2. ✅ Configure environment variables
3. ✅ Test with LiveKit Playground
4. ✅ Deploy webhook server (Render/other cloud)
5. ✅ Configure Twilio webhook
6. ✅ Make test call
7. ✅ Monitor metrics and optimize

## Support

- **LiveKit Docs**: https://docs.livekit.io/agents/ops/deployment
- **LiveKit Cloud**: https://cloud.livekit.io
- **Community**: https://github.com/livekit/agents/discussions
- **Discord**: LiveKit Discord server

## Quick Reference

```bash
# Authenticate
lk cloud auth

# Deploy agent
lk agent deploy

# View logs
lk agent logs <agent-name>

# List agents
lk agent list

# Update agent
lk agent update <agent-name> --env VAR=value

# Delete agent
lk agent delete <agent-name>
```

---

**Note:** The webhook server (`webhook.py`) should still be deployed separately (e.g., Render.com) as it needs to handle Twilio webhooks. Only the agent (`agent.py`) runs on LiveKit Cloud.

