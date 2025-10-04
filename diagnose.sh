#!/bin/bash
# diagnose.sh - Debug Docker Desktop MCP registration

echo "🔍 Docker Desktop MCP Diagnostic"
echo "="*70

echo ""
echo "1️⃣  Checking catalog directory..."
if [ -d "$HOME/.docker/mcp/catalogs/unsafe-browser-mcp" ]; then
    echo "✅ Catalog directory exists"
    ls -la "$HOME/.docker/mcp/catalogs/unsafe-browser-mcp/"
else
    echo "❌ Catalog directory NOT found"
    echo "   Expected: $HOME/.docker/mcp/catalogs/unsafe-browser-mcp"
fi

echo ""
echo "2️⃣  Checking catalog.json..."
if [ -f "$HOME/.docker/mcp/catalogs/unsafe-browser-mcp/catalog.json" ]; then
    echo "✅ catalog.json exists"
    echo "Content:"
    cat "$HOME/.docker/mcp/catalogs/unsafe-browser-mcp/catalog.json"
else
    echo "❌ catalog.json NOT found"
fi

echo ""
echo "3️⃣  Checking registry.yaml..."
if [ -f "$HOME/.docker/mcp/registry.yaml" ]; then
    echo "✅ registry.yaml exists"
    echo "Content:"
    cat "$HOME/.docker/mcp/registry.yaml"
else
    echo "❌ registry.yaml NOT found"
fi

echo ""
echo "4️⃣  Checking Docker image..."
if docker images | grep -q "unsafe-browser-mcp"; then
    echo "✅ Docker image exists"
    docker images | grep unsafe-browser-mcp
else
    echo "❌ Docker image NOT found"
    echo "   Run: docker build -t unsafe-browser-mcp:latest ."
fi

echo ""
echo "5️⃣  Checking other MCP catalogs for comparison..."
echo "Other catalogs in directory:"
ls -la "$HOME/.docker/mcp/catalogs/" 2>/dev/null || echo "No catalogs directory found"

echo ""
echo "6️⃣  Checking Docker Desktop version..."
docker --version

echo ""
echo "7️⃣  Checking if Docker Desktop is running..."
if docker info > /dev/null 2>&1; then
    echo "✅ Docker Desktop is running"
else
    echo "❌ Docker Desktop is NOT running"
fi

echo ""
echo "="*70
echo "📋 Summary:"
echo ""
echo "For unsafe-browser to appear in Docker Desktop MCP Toolkit, you need:"
echo "  1. Catalog: ~/.docker/mcp/catalogs/unsafe-browser-mcp/catalog.json"
echo "  2. Registry entry: unsafe-browser: ref: \"\" in registry.yaml"
echo "  3. Docker image: unsafe-browser-mcp:latest"
echo "  4. Docker Desktop restarted"
echo ""
echo "If all checks pass but it still doesn't appear:"
echo "  - Try completely quitting and reopening Docker Desktop"
echo "  - Check Docker Desktop > Settings > Features > Show experimental features"
echo "  - Look for MCP Toolkit settings or beta features"
echo "="*70
