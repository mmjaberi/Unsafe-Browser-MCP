#!/bin/bash
# setup-claude-desktop.sh - Setup MCP integration with Claude Desktop

echo "🔌 Setting up MCP Integration with Claude Desktop"
echo "="*70

# Step 1: Build Docker image
echo ""
echo "📦 Step 1: Building Docker image..."
docker build -t unsafe-browser-mcp:latest .

if [ $? -ne 0 ]; then
    echo "❌ Docker build failed!"
    exit 1
fi

echo "✅ Docker image built successfully"

# Step 2: Detect OS and config path
echo ""
echo "📁 Step 2: Detecting Claude Desktop config location..."

if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    CONFIG_DIR="$HOME/Library/Application Support/Claude"
    CONFIG_FILE="$CONFIG_DIR/claude_desktop_config.json"
    echo "Detected: macOS"
elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    # Windows
    CONFIG_DIR="$APPDATA/Claude"
    CONFIG_FILE="$CONFIG_DIR/claude_desktop_config.json"
    echo "Detected: Windows"
else
    # Linux
    CONFIG_DIR="$HOME/.config/Claude"
    CONFIG_FILE="$CONFIG_DIR/claude_desktop_config.json"
    echo "Detected: Linux"
fi

echo "Config file: $CONFIG_FILE"

# Step 3: Create config directory if needed
mkdir -p "$CONFIG_DIR"

# Step 4: Get current directory
CURRENT_DIR="$(pwd)"
echo "Project directory: $CURRENT_DIR"

# Step 5: Create or update config
echo ""
echo "⚙️  Step 3: Creating MCP configuration..."

# Check if config exists
if [ -f "$CONFIG_FILE" ]; then
    echo "⚠️  Config file already exists. Creating backup..."
    cp "$CONFIG_FILE" "$CONFIG_FILE.backup.$(date +%Y%m%d_%H%M%S)"
fi

# Create config
cat > "$CONFIG_FILE" << EOF
{
  "mcpServers": {
    "unsafe-browser": {
      "command": "docker",
      "args": [
        "run",
        "--rm",
        "-i",
        "--network", "host",
        "-v", "$CURRENT_DIR/downloads:/app/downloads",
        "-v", "$CURRENT_DIR/screenshots:/app/screenshots",
        "-v", "$CURRENT_DIR/logs:/app/logs",
        "-v", "$CURRENT_DIR/sessions:/app/sessions",
        "unsafe-browser-mcp:latest",
        "python",
        "mcp_server.py"
      ]
    }
  }
}
EOF

echo "✅ Configuration created"

# Step 6: Show completion message
echo ""
echo "="*70
echo "🎉 Setup Complete!"
echo "="*70
echo ""
echo "Next steps:"
echo "1. Restart Claude Desktop"
echo "2. The browser tools should be available"
echo "3. Try asking Claude: 'What browser tools do you have?'"
echo ""
echo "Configuration file: $CONFIG_FILE"
echo ""
echo "To test manually:"
echo "docker run --rm -i unsafe-browser-mcp:latest python mcp_server.py"
echo ""
echo "="*70
