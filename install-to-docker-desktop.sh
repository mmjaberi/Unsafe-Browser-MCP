#!/bin/bash
# install-to-docker-desktop.sh - FIXED VERSION
# Register Unsafe Browser MCP with Docker Desktop's MCP Toolkit

echo "🐳 Installing to Docker Desktop MCP Toolkit"
echo "="*70

PROJECT_DIR="$(pwd)"
CATALOG_DIR="$HOME/.docker/mcp/catalogs/unsafe-browser-mcp"
REGISTRY_FILE="$HOME/.docker/mcp/registry.yaml"

# Step 1: Build Docker image
echo ""
echo "📦 Step 1: Building Docker image..."
docker build -t unsafe-browser-mcp:latest .

if [ $? -ne 0 ]; then
    echo "❌ Docker build failed!"
    exit 1
fi

echo "✅ Docker image built successfully"

# Step 2: Create catalog directory and files
echo ""
echo "📁 Step 2: Creating catalog..."
mkdir -p "$CATALOG_DIR"

# Create catalog.json
cat > "$CATALOG_DIR/catalog.json" << EOF
{
  "name": "unsafe-browser-mcp",
  "version": "2.0.0",
  "description": "Browser automation with SSL bypass for testing and development",
  "author": "Mohammed Al Jaberi",
  "server": {
    "type": "docker",
    "image": "unsafe-browser-mcp:latest",
    "command": "python",
    "args": ["mcp_server.py"],
    "volumes": [
      {
        "host": "$PROJECT_DIR/downloads",
        "container": "/app/downloads"
      },
      {
        "host": "$PROJECT_DIR/screenshots",
        "container": "/app/screenshots"
      },
      {
        "host": "$PROJECT_DIR/logs",
        "container": "/app/logs"
      },
      {
        "host": "$PROJECT_DIR/sessions",
        "container": "/app/sessions"
      }
    ],
    "environment": {
      "PYTHONUNBUFFERED": "1"
    }
  },
  "tools": [
    {
      "name": "browser_navigate",
      "description": "Navigate to a URL in the browser"
    },
    {
      "name": "browser_click",
      "description": "Click element (supports smart keywords)"
    },
    {
      "name": "browser_fill",
      "description": "Fill input fields"
    },
    {
      "name": "browser_screenshot",
      "description": "Take screenshots"
    },
    {
      "name": "browser_save_session",
      "description": "Save browser session"
    },
    {
      "name": "browser_load_session",
      "description": "Load browser session"
    }
  ]
}
EOF

echo "✅ Catalog created at $CATALOG_DIR"

# Step 3: Update registry.yaml to reference the catalog (like other MCPs)
echo ""
echo "⚙️  Step 3: Updating registry.yaml..."

mkdir -p "$HOME/.docker/mcp"

# Backup if exists
if [ -f "$REGISTRY_FILE" ]; then
    cp "$REGISTRY_FILE" "$REGISTRY_FILE.backup.$(date +%Y%m%d_%H%M%S)"
    echo "✅ Backed up existing registry.yaml"
fi

# Check if registry exists
if [ ! -f "$REGISTRY_FILE" ]; then
    # Create new registry with just the reference
    cat > "$REGISTRY_FILE" << 'EOF'
registry:
  curl:
    ref: ""
  desktop-commander:
    ref: ""
  duckduckgo:
    ref: ""
  filesystem:
    ref: ""
  google-maps:
    ref: ""
  playwright:
    ref: ""
  puppeteer:
    ref: ""
  youtube_transcript:
    ref: ""
  unsafe-browser:
    ref: ""
EOF
else
    # Check if unsafe-browser already exists
    if grep -q "unsafe-browser:" "$REGISTRY_FILE"; then
        echo "⚠️  'unsafe-browser' already exists, updating..."
        # Remove the old entry and everything under it
        sed -i.tmp '/unsafe-browser:/,/^[^ ]/d' "$REGISTRY_FILE"
    fi
    
    # Add the simple reference (like other MCPs)
    cat >> "$REGISTRY_FILE" << 'EOF'
  unsafe-browser:
    ref: ""
EOF
fi

echo "✅ Registry updated"

# Step 4: Verify
echo ""
echo "✅ Step 4: Verifying installation..."

if [ -f "$CATALOG_DIR/catalog.json" ]; then
    echo "✅ Catalog exists"
else
    echo "❌ Catalog not found"
    exit 1
fi

if grep -q "unsafe-browser:" "$REGISTRY_FILE"; then
    echo "✅ Registry entry exists"
else
    echo "❌ Registry entry not found"
    exit 1
fi

# Step 5: Show completion
echo ""
echo "="*70
echo "🎉 Installation Complete!"
echo "="*70
echo ""
echo "📍 Files created:"
echo "   Catalog: $CATALOG_DIR/catalog.json"
echo "   Registry: $REGISTRY_FILE"
echo ""
echo "Next steps:"
echo "1. Restart Docker Desktop"
echo "2. Open Docker Desktop → MCP Toolkit"
echo "3. You should see 'Unsafe Browser' in the list"
echo "4. Click to start the server"
echo ""
echo "To verify:"
echo "cat $REGISTRY_FILE"
echo "cat $CATALOG_DIR/catalog.json"
echo ""
echo "="*70
