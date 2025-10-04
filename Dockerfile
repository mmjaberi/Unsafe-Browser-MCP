# Enhanced Dockerfile for Unsafe Browser MCP Server
# Now with MCP support for Claude Desktop integration

FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    ca-certificates \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libatspi2.0-0 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libgbm1 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libwayland-client0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxkbcommon0 \
    libxrandr2 \
    xdg-utils \
    libu2f-udev \
    libvulkan1 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers
RUN playwright install chromium
RUN playwright install-deps chromium

# Copy application files
COPY simple_unsafe_fetch.py .
COPY unsafe_browser_mcp.py .
COPY practical_examples.py .
COPY enhanced_simple_fetcher.py .
COPY enhanced_browser_mcp.py .
COPY mcp_server.py .

# Create directories for outputs
RUN mkdir -p /app/downloads /app/screenshots /app/logs /app/sessions

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV DISPLAY=:99

# Expose port for MCP server
EXPOSE 8000

# Default command - MCP server for Claude Desktop
CMD ["python", "mcp_server.py"]
