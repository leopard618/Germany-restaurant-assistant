# Render.com Deployment Guide

Complete guide for deploying the Restaurant Reservation Voice AI Agent on Render.com.

## Prerequisites

- Render.com account (sign up at https://render.com)
- GitHub repository with your code
- Twilio account with phone number
- LiveKit Cloud account
- OpenAI API key

## Deployment Steps

### Step 1: Prepare Repository

1. Push your code to GitHub
2. Ensure all files are committed:
   - `agent.py`
   - `webhook.py`
   - `config.py`
   - `requirements.txt`
   - `render.yaml` (optional, for automated setup)

### Step 2: Create Webhook Service

1. Go to Render Dashboard → **New** → **Web Service**
2. Connect your GitHub repository
3. Configure service:
   - **Name**: `webhook-server`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python webhook.py`
   - **Plan**: Choose appropriate plan (Starter for testing)

4. Add Environment Variables:
   ```
   TWILIO_ACCOUNT_SID=your_account_sid
   TWILIO_AUTH_TOKEN=your_auth_token
   TWILIO_PHONE_NUMBER=your_phone_number
   LIVEKIT_URL=wss://your-project.livekit.cloud
   LIVEKIT_API_KEY=your_api_key
   LIVEKIT_API_SECRET=your_api_secret
   OPENAI_API_KEY=your_openai_key
   LOG_LEVEL=INFO
   WEBHOOK_HOST=0.0.0.0
   ```

5. Click **Create Web Service**

### Step 3: Create Agent Worker

1. Go to Render Dashboard → **New** → **Background Worker**
2. Connect same GitHub repository
3. Configure worker:
   - **Name**: `ai-agent`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python agent.py`
   - **Plan**: Choose appropriate plan

4. Add Environment Variables:
   ```
   LIVEKIT_URL=wss://your-project.livekit.cloud
   LIVEKIT_API_KEY=your_api_key
   LIVEKIT_API_SECRET=your_api_secret
   OPENAI_API_KEY=your_openai_key
   LOG_LEVEL=INFO
   ```

5. Click **Create Background Worker**

### Step 4: Get Webhook URL

1. After webhook service deploys, go to service dashboard
2. Copy the service URL (e.g., `https://webhook-server.onrender.com`)
3. Your webhook endpoint will be: `https://webhook-server.onrender.com/webhook/incoming`

### Step 5: Configure Twilio

1. Go to Twilio Console → **Phone Numbers** → **Active numbers**
2. Click your phone number
3. Scroll to **Voice Configuration**
4. Under "A CALL COMES IN":
   - Select **Webhook**
   - Enter: `https://webhook-server.onrender.com/webhook/incoming`
   - Method: **HTTP POST**
5. Click **Save**

### Step 6: Verify Deployment

1. Check both services are running (green status)
2. Review logs for any errors
3. Make a test call to your Twilio number
4. Monitor logs in real-time

## Using render.yaml (Alternative)

If you have `render.yaml` in your repository:

1. Go to Render Dashboard → **New** → **Blueprint**
2. Connect your GitHub repository
3. Render will automatically detect `render.yaml`
4. Review and confirm services
5. Add environment variables (same as above)
6. Deploy

## Environment Variables Reference

### Webhook Service
- `TWILIO_ACCOUNT_SID` - Twilio Account SID
- `TWILIO_AUTH_TOKEN` - Twilio Auth Token
- `TWILIO_PHONE_NUMBER` - Your Twilio phone number
- `LIVEKIT_URL` - LiveKit WebSocket URL
- `LIVEKIT_API_KEY` - LiveKit API Key
- `LIVEKIT_API_SECRET` - LiveKit API Secret
- `OPENAI_API_KEY` - OpenAI API Key
- `LOG_LEVEL` - Logging level (INFO, DEBUG, etc.)
- `WEBHOOK_HOST` - Host address (0.0.0.0)

### Agent Worker
- `LIVEKIT_URL` - LiveKit WebSocket URL
- `LIVEKIT_API_KEY` - LiveKit API Key
- `LIVEKIT_API_SECRET` - LiveKit API Secret
- `OPENAI_API_KEY` - OpenAI API Key
- `LOG_LEVEL` - Logging level

## Important Notes

1. **Port Configuration**: Render automatically provides `PORT` environment variable. The code uses this automatically.

2. **HTTPS**: Render provides HTTPS automatically. No SSL configuration needed.

3. **Auto-Deploy**: Services auto-deploy on git push (if enabled).

4. **Scaling**: 
   - Webhook service: Scale based on concurrent calls
   - Agent worker: Can run multiple instances for load distribution

5. **Logs**: Access logs from Render dashboard for debugging.

6. **Costs**: 
   - Free tier: Services sleep after 15 minutes of inactivity
   - Paid plans: Always-on services

## Troubleshooting

### Service won't start
- Check build logs for dependency issues
- Verify all environment variables are set
- Check Python version compatibility

### Webhook not receiving calls
- Verify webhook URL in Twilio matches Render service URL
- Check service is running (not sleeping)
- Review webhook service logs

### Agent not connecting
- Verify agent worker is running
- Check LiveKit credentials
- Review agent worker logs

### High latency
- Use Render region closest to users
- Consider upgrading to paid plan (always-on)
- Check LiveKit region selection

## Monitoring

1. **Render Dashboard**: Monitor service health and logs
2. **Twilio Console**: Monitor call logs and usage
3. **LiveKit Dashboard**: Monitor active sessions
4. **Application Logs**: Check both service logs for errors

## Production Recommendations

1. **Upgrade to Paid Plan**: Ensures services stay awake
2. **Enable Auto-Deploy**: For seamless updates
3. **Set Up Alerts**: Monitor service health
4. **Use Custom Domain**: For production (optional)
5. **Enable Metrics**: Monitor performance

## Support

- Render Docs: https://render.com/docs
- Render Status: https://status.render.com
- Render Community: https://community.render.com

