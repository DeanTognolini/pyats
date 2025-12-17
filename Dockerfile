# Use a specific Python version for reproducibility
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

# Install system dependencies and Python packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        iputils-ping \
        openssh-client \
        git && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

CMD ["bash"]
