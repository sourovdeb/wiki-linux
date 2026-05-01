FROM mcr.microsoft.com/vscode/devcontainers/python:3.11

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    ripgrep \
    glow \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /workspace

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Optional: install ollama client for when ollama service is available
RUN pip install --no-cache-dir ollama

# Set up entrypoint to offer ingest on first launch
COPY .devcontainer/setup.sh /setup.sh
RUN chmod +x /setup.sh

# The shell will run setup.sh on first terminal open
ENV SHELL=/bin/bash
