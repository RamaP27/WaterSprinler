# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Explicitly copy model files if they exist (helps ensure they're included)
# Note: These will be copied by COPY . . above, but this helps with debugging
RUN ls -la /app/ | grep -E "(sprinkler_lstm|artifacts)" || echo "Note: Model files will be available at runtime if trained"

# Expose port
EXPOSE 8080

# Run the application
# Increased timeout to 600 seconds (10 minutes) to handle model training
# Cloud Run timeout is 300s, but we set gunicorn higher to handle edge cases
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "2", "--timeout", "600", "--graceful-timeout", "30", "main:app"]

