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

