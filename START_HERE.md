# 🚀 START HERE - Docker Desktop MCP Toolkit Setup

## What You Want
Show "Unsafe Browser" in Docker Desktop's MCP Toolkit (like your other MCPs)

## Simple 3-Step Setup

### Step 1: Build
```bash
cd ~/Desktop/unsafe-browser-mcp
docker build -t unsafe-browser-mcp:latest .
```

### Step 2: Install
```bash
chmod +x install-to-docker-desktop.sh
./install-to-docker-desktop.sh
```

### Step 3: Refresh Docker Desktop
1. Open Docker Desktop
2. Click "MCP Toolkit" in sidebar
3. Refresh or restart Docker Desktop
4. See "Unsafe Browser" in your servers list! ✅

## That's It!

Your MCP now appears in Docker Desktop alongside:
- curl
- Desktop Commander  
- DuckDuckGo
- etc.

## Using It

1. **Start in Docker Desktop**: Click the start button next to "Unsafe Browser"
2. **Use in Claude Desktop**: Ask Claude "What browser tools do you have?"
3. **Test**: "Navigate to example.com and take a screenshot"

## What It Does

Adds your server to: `~/.docker/mcp/registry.yaml`

You do NOT need to:
- ❌ Edit any files manually
- ❌ Run HTTP servers
- ❌ Configure Claude Desktop separately
- ❌ Use bridge scripts

Just run the 3 steps above! 🎉

## Troubleshooting

**Not showing up?**
- Restart Docker Desktop completely
- Check: `cat ~/.docker/mcp/registry.yaml | grep unsafe-browser`
- Verify image: `docker images | grep unsafe-browser-mcp`

**Need help?**
See: Docker Desktop MCP Toolkit Integration Guide (in artifacts)
