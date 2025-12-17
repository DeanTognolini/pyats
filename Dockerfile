# =============================================================================
# pyATS Layer 1 Validation Docker Image
# =============================================================================
#
# Build:
#   docker build -t pyats-layer1 .
#
# Run with volume mounts:
#   docker run -it --rm \
#     -v $(pwd)/testbed.yaml:/app/testbed.yaml:ro \
#     -v $(pwd)/reports:/app/reports \
#     -e PYATS_USERNAME="admin" \
#     -e PYATS_PASSWORD="password" \
#     pyats-layer1 \
#     pyats run job layer1_job.py --testbed testbed.yaml --html-logs /app/reports/
#
# =============================================================================

# Use a specific Python version for reproducibility
FROM python:3.11-slim

# Set metadata
LABEL maintainer="pyats-layer1"
LABEL description="pyATS Layer 1 Network Validation Framework"
LABEL version="1.0"

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install system dependencies and Python packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        iputils-ping \
        openssh-client \
        git \
        vim \
        less && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    pip install --no-cache-dir -r requirements.txt

# Create directories for volume mounts
RUN mkdir -p /app/reports /app/archive /app/logs && \
    chmod 777 /app/reports /app/archive /app/logs

# Copy application code
COPY layer1_job.py layer1_tests.py ./

# Copy sample testbed (will be overridden by volume mount in production)
COPY testbed.yaml ./testbed.yaml.example

# Set environment variables with sensible defaults
ENV PYATS_LOG_LEVEL=INFO \
    PYATS_REPORT_DIR=/app/reports \
    PYTHONUNBUFFERED=1

# Define volume mount points
# These allow users to mount their own testbed and preserve reports
VOLUME ["/app/testbed.yaml", "/app/reports", "/app/archive"]

# Health check (optional - verifies Python and pyATS are working)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import pyats; print('pyATS OK')" || exit 1

# Default command: Interactive bash shell
# Override with pyATS commands when running
CMD ["bash"]

# Common usage examples (for reference):
#
# Interactive mode:
#   docker run -it --rm pyats-layer1
#
# Run tests with mounted testbed:
#   docker run --rm \
#     -v $(pwd)/testbed.yaml:/app/testbed.yaml:ro \
#     -v $(pwd)/reports:/app/reports \
#     -e PYATS_USERNAME="${PYATS_USERNAME}" \
#     -e PYATS_PASSWORD="${PYATS_PASSWORD}" \
#     pyats-layer1 \
#     pyats run job layer1_job.py --testbed testbed.yaml --html-logs /app/reports/
#
# Run with custom log level:
#   docker run --rm \
#     -v $(pwd)/testbed.yaml:/app/testbed.yaml:ro \
#     -v $(pwd)/reports:/app/reports \
#     -e PYATS_USERNAME="${PYATS_USERNAME}" \
#     -e PYATS_PASSWORD="${PYATS_PASSWORD}" \
#     pyats-layer1 \
#     pyats run job layer1_job.py --testbed testbed.yaml --loglevel DEBUG

