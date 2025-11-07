# Deployment Guide (Without Docker)

Deploy your agent to cloud platforms that support direct Python deployment without Docker.

## Available Options

### Option 1: Render.com (Recommended) ⭐

**Best for:** Easy deployment, free tier available, good for low latency

**Pros:**
- ✅ No Docker required
- ✅ Direct Python deployment
- ✅ Free tier available
- ✅ Auto-deploy from GitHub
- ✅ HTTPS included
- ✅ Multiple regions available

**Cons:**
- ⚠️ Free tier sleeps after 15 min inactivity
- ⚠️ Cold start latency on free tier

**Deployment Steps:**

1. **Push code to GitHub**
   ```bash
   git add .
   git commit -m "Ready for deployment"
   git push origin main
   ```

2. **Create Webhook Service on Render**
   - Go to https://render.com
   - Click **New** → **Web Service**
   - Connect your GitHub repository
   - Configure:
     - **Name**: `webhook-server`
     - **Environment**: `Python 3`
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `python webhook.py`
     - **Plan**: Choose plan (Starter for testing)

3. **Add Environment Variables:**
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

4. **Create Agent Worker on Render**
   - Click **New** → **Background Worker**
   - Connect same GitHub repository
   - Configure:
     - **Name**: `ai-agent`
     - **Environment**: `Python 3`
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `python agent.py`
     - **Plan**: Choose plan

5. **Add Environment Variables:**
   ```
   LIVEKIT_URL=wss://your-project.livekit.cloud
   LIVEKIT_API_KEY=your_api_key
   LIVEKIT_API_SECRET=your_api_secret
   OPENAI_API_KEY=your_openai_key
   LOG_LEVEL=INFO
   VOICE_MODEL=shimmer
   ```

6. **Deploy**
   - Click **Create** on both services
   - Wait for deployment (2-5 minutes)
   - Check logs to verify

**See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed Render.com guide.**

---

### Option 2: Railway.app

**Best for:** Simple deployment, good developer experience

**Pros:**
- ✅ No Docker required
- ✅ Direct Python support
- ✅ Simple UI
- ✅ Auto-deploy from GitHub
- ✅ Free tier available ($5 credit/month)

**Cons:**
- ⚠️ Limited free tier
- ⚠️ May require Dockerfile for some cases

**Deployment Steps:**

1. **Install Railway CLI** (optional)
   ```bash
   npm install -g @railway/cli
   ```

2. **Deploy via Dashboard:**
   - Go to https://railway.app
   - Click **New Project**
   - Select **Deploy from GitHub repo**
   - Choose your repository

3. **Create Two Services:**

   **Service 1: Webhook Server**
   - Add service → **GitHub Repo**
   - Configure:
     - **Root Directory**: `/`
     - **Start Command**: `python webhook.py`
   - Add environment variables (same as Render)

   **Service 2: Agent Worker**
   - Add service → **GitHub Repo**
   - Configure:
     - **Root Directory**: `/`
     - **Start Command**: `python agent.py`
   - Add environment variables

4. **Deploy**
   - Railway auto-detects Python and installs dependencies
   - Services will deploy automatically

---

### Option 3: Fly.io

**Best for:** Global distribution, low latency

**Pros:**
- ✅ No Docker required (can use buildpacks)
- ✅ Global edge locations
- ✅ Good for low latency
- ✅ Free tier available

**Cons:**
- ⚠️ Requires `fly.toml` configuration
- ⚠️ CLI-based deployment

**Deployment Steps:**

1. **Install Fly CLI**
   ```bash
   # Windows (PowerShell)
   powershell -Command "iwr https://fly.io/install.ps1 -useb | iex"
   
   # macOS/Linux
   curl -L https://fly.io/install.sh | sh
   ```

2. **Login**
   ```bash
   fly auth login
   ```

3. **Create Apps**
   ```bash
   # Create webhook app
   fly launch --name webhook-server --no-deploy
   
   # Create agent app
   fly launch --name ai-agent --no-deploy
   ```

4. **Configure `fly.toml` for Webhook:**
   ```toml
   app = "webhook-server"
   primary_region = "iad"  # Choose closest region
   
   [build]
   
   [http_service]
     internal_port = 8080
     force_https = true
     auto_stop_machines = false
     auto_start_machines = true
   
   [[services]]
     protocol = "tcp"
     internal_port = 8080
   ```

5. **Configure `fly.toml` for Agent:**
   ```toml
   app = "ai-agent"
   primary_region = "iad"  # Choose closest region
   
   [build]
   
   [processes]
     agent = "python agent.py"
   ```

6. **Set Secrets**
   ```bash
   # Webhook secrets
   fly secrets set -a webhook-server \
     TWILIO_ACCOUNT_SID=xxx \
     TWILIO_AUTH_TOKEN=xxx \
     ...
   
   # Agent secrets
   fly secrets set -a ai-agent \
     LIVEKIT_URL=xxx \
     LIVEKIT_API_KEY=xxx \
     ...
   ```

7. **Deploy**
   ```bash
   fly deploy -a webhook-server
   fly deploy -a ai-agent
   ```

---

### Option 4: Heroku

**Best for:** Traditional PaaS, well-documented

**Pros:**
- ✅ No Docker required
- ✅ Direct Python support
- ✅ Well-documented
- ✅ Add-ons ecosystem

**Cons:**
- ⚠️ Free tier discontinued
- ⚠️ Paid plans required
- ⚠️ Requires `Procfile`

**Deployment Steps:**

1. **Install Heroku CLI**
   ```bash
   # Download from https://devcenter.heroku.com/articles/heroku-cli
   ```

2. **Create `Procfile`**
   ```
   webhook: python webhook.py
   agent: python agent.py
   ```

3. **Create `runtime.txt`** (optional)
   ```
   python-3.11.0
   ```

4. **Login**
   ```bash
   heroku login
   ```

5. **Create Apps**
   ```bash
   # Webhook app
   heroku create webhook-server
   
   # Agent app
   heroku create ai-agent
   ```

6. **Set Environment Variables**
   ```bash
   # Webhook
   heroku config:set -a webhook-server \
     TWILIO_ACCOUNT_SID=xxx \
     ...
   
   # Agent
   heroku config:set -a ai-agent \
     LIVEKIT_URL=xxx \
     ...
   ```

7. **Deploy**
   ```bash
   git push heroku main
   ```

---

### Option 5: DigitalOcean App Platform

**Best for:** Simple deployment, good pricing

**Pros:**
- ✅ No Docker required
- ✅ Direct Python support
- ✅ Simple UI
- ✅ Good pricing

**Cons:**
- ⚠️ Requires configuration file

**Deployment Steps:**

1. **Create `app.yaml`**
   ```yaml
   name: restaurant-assistant
   services:
     - name: webhook
       github:
         repo: yourusername/your-repo
         branch: main
       run_command: python webhook.py
       environment_slug: python
       instance_count: 1
       instance_size_slug: basic-xxs
       envs:
         - key: TWILIO_ACCOUNT_SID
           value: ${TWILIO_ACCOUNT_SID}
         # ... other env vars
   
     - name: agent
       github:
         repo: yourusername/your-repo
         branch: main
       run_command: python agent.py
       environment_slug: python
       instance_count: 1
       instance_size_slug: basic-xxs
       envs:
         - key: LIVEKIT_URL
           value: ${LIVEKIT_URL}
         # ... other env vars
   ```

2. **Deploy via Dashboard:**
   - Go to https://cloud.digitalocean.com
   - Click **Create** → **App Platform**
   - Upload `app.yaml` or connect GitHub
   - Configure and deploy

---

### Option 6: AWS/GCP/Azure (VMs)

**Best for:** Full control, custom infrastructure

**Pros:**
- ✅ Full control
- ✅ No Docker required
- ✅ Can optimize for low latency
- ✅ Scalable

**Cons:**
- ⚠️ Requires server management
- ⚠️ More complex setup
- ⚠️ Need to handle scaling manually

**Quick Setup (AWS EC2 Example):**

1. **Launch EC2 Instance**
   - Choose Ubuntu/Debian
   - Select instance type (t3.micro for testing)
   - Configure security group (allow HTTP/HTTPS)

2. **SSH into Instance**
   ```bash
   ssh -i your-key.pem ubuntu@your-instance-ip
   ```

3. **Install Dependencies**
   ```bash
   sudo apt update
   sudo apt install python3-pip python3-venv git -y
   ```

4. **Clone and Setup**
   ```bash
   git clone https://github.com/yourusername/your-repo.git
   cd your-repo
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

5. **Create Systemd Services**

   **`/etc/systemd/system/webhook.service`:**
   ```ini
   [Unit]
   Description=Webhook Server
   After=network.target
   
   [Service]
   Type=simple
   User=ubuntu
   WorkingDirectory=/home/ubuntu/your-repo
   Environment="PATH=/home/ubuntu/your-repo/venv/bin"
   ExecStart=/home/ubuntu/your-repo/venv/bin/python webhook.py
   Restart=always
   
   [Install]
   WantedBy=multi-user.target
   ```

   **`/etc/systemd/system/agent.service`:**
   ```ini
   [Unit]
   Description=AI Agent
   After=network.target
   
   [Service]
   Type=simple
   User=ubuntu
   WorkingDirectory=/home/ubuntu/your-repo
   Environment="PATH=/home/ubuntu/your-repo/venv/bin"
   ExecStart=/home/ubuntu/your-repo/venv/bin/python agent.py
   Restart=always
   
   [Install]
   WantedBy=multi-user.target
   ```

6. **Set Environment Variables**
   ```bash
   # Create .env file or use systemd Environment directives
   sudo nano /etc/systemd/system/webhook.service
   # Add Environment="VAR=value" lines
   ```

7. **Start Services**
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable webhook agent
   sudo systemctl start webhook agent
   ```

8. **Setup Nginx (for webhook)**
   ```bash
   sudo apt install nginx -y
   # Configure nginx to proxy to webhook server
   ```

---

## Comparison Table

| Platform | Docker Required | Free Tier | Ease of Use | Low Latency | Best For |
|----------|----------------|-----------|-------------|-------------|----------|
| **Render.com** | ❌ No | ✅ Yes | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | General use |
| **Railway** | ❌ No | ✅ Limited | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | Simple deployment |
| **Fly.io** | ❌ No* | ✅ Yes | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Global distribution |
| **Heroku** | ❌ No | ❌ No | ⭐⭐⭐⭐ | ⭐⭐⭐ | Traditional PaaS |
| **DigitalOcean** | ❌ No | ❌ No | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | Good pricing |
| **AWS/GCP/Azure** | ❌ No | ⚠️ Limited | ⭐⭐ | ⭐⭐⭐⭐⭐ | Full control |

*Fly.io can use buildpacks instead of Docker

## Recommendations for Low Latency

1. **Best Overall:** Render.com or Railway
   - Easy to deploy
   - No Docker needed
   - Good performance
   - Free tier available

2. **Best for Global:** Fly.io
   - Edge locations worldwide
   - Lowest latency globally
   - Requires more setup

3. **Best for Control:** AWS/GCP/Azure
   - Full control over infrastructure
   - Can optimize everything
   - Requires more management

## Quick Start (Render.com - Easiest)

1. Push code to GitHub
2. Go to https://render.com
3. Create Web Service → Connect GitHub → Select repo
4. Set start command: `python webhook.py`
5. Add environment variables
6. Create Background Worker → Same repo
7. Set start command: `python agent.py`
8. Add environment variables
9. Deploy!

**That's it!** No Docker needed.

---

## Notes

- **Webhook Server** needs to be accessible via HTTPS (for Twilio)
- **Agent Worker** only needs to connect to LiveKit (no public endpoint)
- Both services can run on the same platform or different platforms
- For lowest latency, deploy both in the same region as your LiveKit Cloud project

## Support

- **Render Docs**: https://render.com/docs
- **Railway Docs**: https://docs.railway.app
- **Fly.io Docs**: https://fly.io/docs
- **Heroku Docs**: https://devcenter.heroku.com

