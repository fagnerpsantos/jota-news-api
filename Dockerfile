# syntax=docker/dockerfile:1

FROM python:3.12-slim

# Prevents Python from writing pyc files and buffering stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    postgresql-client \
    iputils-ping \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY pyproject.toml uv.lock ./
RUN pip install --no-cache-dir uv && \
    uv pip install --system -e .

# Copy project
COPY . .

# Make entrypoint script executable
RUN chmod +x entrypoint.sh

# Run as non-root user
RUN useradd -m appuser
RUN chown -R appuser:appuser /app
USER appuser

# Expose the port
EXPOSE 8000

# Command to run the application
CMD ["./entrypoint.sh"]
