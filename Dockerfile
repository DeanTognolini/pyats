# =============================================================================
# pyATS Network Testing Framework Docker Image
# =============================================================================
#
# Build:
#   docker build -t pyats-network-tests .
#
# Run with volume mounts:
#   docker run -it --rm \
#     -v $(pwd)/testbeds:/app/testbeds:ro \
#     -v $(pwd)/reports:/app/reports \
#     -e PYATS_USERNAME="admin" \
#     -e PYATS_PASSWORD="password" \
#     pyats-network-tests \
#     pyats run job jobs/run_all.py --testbed testbeds/testbed.yaml --html-logs /app/reports/
#
# =============================================================================

# Use a specific Python version for reproducibility
FROM python:3.11-slim

# Set metadata
LABEL maintainer="pyats-network-tests"
LABEL description="pyATS Network Testing Framework - Template Repository"
LABEL version="1.0"

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        iputils-ping \
        openssh-client \
        git \
        vim \
        less \
        gcc \
        g++ \
        make \
        libffi-dev \
        libssl-dev \
        libxml2-dev \
        libxslt1-dev \
        zlib1g-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install Python packages separately for better error visibility
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# Create directories for volume mounts
RUN mkdir -p /app/reports /app/archive /app/logs && \
    chmod 777 /app/reports /app/archive /app/logs

# Copy application structure
COPY jobs/ ./jobs/
COPY tests/ ./tests/
COPY configs/ ./configs/

# Copy sample testbeds (will be overridden by volume mount in production)
COPY testbeds/ ./testbeds/

# Set environment variables with sensible defaults
ENV PYATS_LOG_LEVEL=INFO \
    PYATS_REPORT_DIR=/app/reports \
    PYTHONUNBUFFERED=1

# Define volume mount points
# These allow users to mount their own testbeds and preserve reports
VOLUME ["/app/testbeds", "/app/reports", "/app/archive"]

# Health check (optional - verifies Python and pyATS are working)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import pyats; print('pyATS OK')" || exit 1

# Default command: Interactive bash shell
# Override with pyATS commands when running
CMD ["bash"]

# Common usage examples (for reference):
#
# Interactive mode:
#   docker run -it --rm pyats-network-tests
#
# Run all test suites:
#   docker run --rm \
#     -v $(pwd)/testbeds:/app/testbeds:ro \
#     -v $(pwd)/reports:/app/reports \
#     -e PYATS_USERNAME="${PYATS_USERNAME}" \
#     -e PYATS_PASSWORD="${PYATS_PASSWORD}" \
#     pyats-network-tests \
#     pyats run job jobs/run_all.py --testbed testbeds/testbed.yaml --html-logs /app/reports/
#
# Run specific test suite (Layer 1):
#   docker run --rm \
#     -v $(pwd)/testbeds:/app/testbeds:ro \
#     -v $(pwd)/reports:/app/reports \
#     -e PYATS_USERNAME="${PYATS_USERNAME}" \
#     -e PYATS_PASSWORD="${PYATS_PASSWORD}" \
#     pyats-network-tests \
#     pyats run job jobs/run_layer1.py --testbed testbeds/testbed.yaml --html-logs /app/reports/
#
# Run with custom log level:
#   docker run --rm \
#     -v $(pwd)/testbeds:/app/testbeds:ro \
#     -v $(pwd)/reports:/app/reports \
#     -e PYATS_USERNAME="${PYATS_USERNAME}" \
#     -e PYATS_PASSWORD="${PYATS_PASSWORD}" \
#     pyats-network-tests \
#     pyats run job jobs/run_all.py --testbed testbeds/testbed.yaml --loglevel DEBUG
