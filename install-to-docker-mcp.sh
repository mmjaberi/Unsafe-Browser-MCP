#!/bin/bash
# install-to-docker-mcp.sh - Install to Docker MCP catalogs

echo "🔌 Installing Unsafe Browser MCP to Docker MCP Catalogs"
echo "="*70

# Configuration
CATALOG_DIR="/Users/mohammedaljaberi/.docker/mcp/catalogs"
MCP_NAME="unsafe-browser-mcp"
PROJECT_DIR="$(pwd)"

# Step 1: Build Docker image
echo ""
echo "📦 Step 1: Building Docker image..."
docker build -t unsafe-browser-mcp:latest .

if [ $? -ne 0 ]; then
    echo "❌ Docker build failed!"
    exit 1
fi

echo "✅ Docker image built successfully"

# Step 2: Create catalog directory
echo ""
echo "📁 Step 2: Creating catalog directory..."
mkdir -p "$CATALOG_DIR/$MCP_NAME"

echo "Catalog directory: $CATALOG_DIR/$MCP_NAME"

# Step 3: Copy catalog.json
echo ""
echo "📄 Step 3: Installing catalog configuration..."
cp catalog.json "$CATALOG_DIR/$MCP_NAME/catalog.json"

# Update PROJECT_DIR in catalog
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    sed -i '' "s|\${PROJECT_DIR}|$PROJECT_DIR|g" "$CATALOG_DIR/$MCP_NAME/catalog.json"
else
    # Linux
    sed -i "s|\${PROJECT_DIR}|$PROJECT_DIR|g" "$CATALOG_DIR/$MCP_NAME/catalog.json"
fi

echo "✅ Catalog installed"

# Step 4: Create Claude Desktop config
echo ""
echo "⚙️  Step 4: Configuring Claude Desktop..."

# Detect OS and config path
if [[ "$OSTYPE" == "darwin"* ]]; then
    CONFIG_DIR="$HOME/Library/Application Support/Claude"
elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    CONFIG_DIR="$APPDATA/Claude"
else
    CONFIG_DIR="$HOME/.config/Claude"
fi

CONFIG_FILE="$CONFIG_DIR/claude_desktop_config.json"
mkdir -p "$CONFIG_DIR"

# Backup existing config
if [ -f "$CONFIG_FILE" ]; then
    echo "⚠️  Backing up existing config..."
    cp "$CONFIG_FILE" "$CONFIG_FILE.backup.$(date +%Y%m%d_%H%M%S)"
    
    # Check if unsafe-browser already exists
    if grep -q '"unsafe-browser"' "$CONFIG_FILE"; then
        echo "⚠️  'unsafe-browser' already exists in config. Updating..."
        
        # Remove old entry and add new one
        python3 -c "
import json
with open('$CONFIG_FILE', 'r') as f:
    config = json.load(f)

config['mcpServers']['unsafe-browser'] = {
    'command': 'docker',
    'args': [
        'run', '--rm', '-i', '--network', 'host',
        '-v', '$PROJECT_DIR/downloads:/app/downloads',
        '-v', '$PROJECT_DIR/screenshots:/app/screenshots',
        '-v', '$PROJECT_DIR/logs:/app/logs',
        '-v', '$PROJECT_DIR/sessions:/app/sessions',
        'unsafe-browser-mcp:latest',
        'python', 'mcp_server.py'
    ]
}

with open('$CONFIG_FILE', 'w') as f:
    json.dump(config, f, indent=2)
"
    else
        # Add to existing config
        python3 -c "
import json
with open('$CONFIG_FILE', 'r') as f:
    config = json.load(f)

if 'mcpServers' not in config:
    config['mcpServers'] = {}

config['mcpServers']['unsafe-browser'] = {
    'command': 'docker',
    'args': [
        'run', '--rm', '-i', '--network', 'host',
        '-v', '$PROJECT_DIR/downloads:/app/downloads',
        '-v', '$PROJECT_DIR/screenshots:/app/screenshots',
        '-v', '$PROJECT_DIR/logs:/app/logs',
        '-v', '$PROJECT_DIR/sessions:/app/sessions',
        'unsafe-browser-mcp:latest',
        'python', 'mcp_server.py'
    ]
}

with open('$CONFIG_FILE', 'w') as f:
    json.dump(config, f, indent=2)
"
    fi
else
    # Create new config
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
        "-v", "$PROJECT_DIR/downloads:/app/downloads",
        "-v", "$PROJECT_DIR/screenshots:/app/screenshots",
        "-v", "$PROJECT_DIR/logs:/app/logs",
        "-v", "$PROJECT_DIR/sessions:/app/sessions",
        "unsafe-browser-mcp:latest",
        "python",
        "mcp_server.py"
      ]
    }
  }
}
EOF
fi

echo "✅ Claude Desktop configured"

# Step 5: Create symlink (optional, for easy updates)
echo ""
echo "🔗 Step 5: Creating symlink for easy updates..."
ln -sf "$PROJECT_DIR" "$CATALOG_DIR/$MCP_NAME/source"
echo "✅ Symlink created"

# Step 6: Verify installation
echo ""
echo "✅ Step 6: Verifying installation..."

echo ""
echo "Catalog location: $CATALOG_DIR/$MCP_NAME"
echo "Project location: $PROJECT_DIR"
echo "Config file: $CONFIG_FILE"

# Step 7: Show completion message
echo ""
echo "="*70
echo "🎉 Installation Complete!"
echo "="*70
echo ""
echo "📍 Installed to: $CATALOG_DIR/$MCP_NAME"
echo ""
echo "Next steps:"
echo "1. Restart Claude Desktop"
echo "2. Ask Claude: 'What browser tools do you have?'"
echo "3. Test: 'Navigate to https://example.com and take a screenshot'"
echo ""
echo "To list all catalogs:"
echo "ls -la $CATALOG_DIR"
echo ""
echo "To view catalog info:"
echo "cat $CATALOG_DIR/$MCP_NAME/catalog.json | jq ."
echo ""
echo "To uninstall:"
echo "rm -rf $CATALOG_DIR/$MCP_NAME"
echo ""
echo "="*70
