# Unsafe Browser MCP - Docker Setup

⚠️ **WARNING**: This tool bypasses SSL certificate verification. Use only for testing/development!

## Files in This Directory

You need to copy 6 more files from the Claude chat artifacts:

### From Artifacts Panel (Right Side):
1. **simple_unsafe_fetch.py** - Click artifact "Simple Unsafe HTTPS Fetch", copy content, save here
2. **unsafe_browser_mcp.py** - Click artifact "Custom MCP Server", copy content, save here  
3. **practical_examples.py** - Click artifact "Practical Examples", copy content, save here
4. **Dockerfile** - Click artifact "Dockerfile", copy content, save here
5. **docker-compose.yml** - Click artifact "docker-compose.yml", copy content, save here

### Already Created:
- ✅ requirements.txt (already here)
- ✅ downloads/ directory (already here)
- ✅ screenshots/ directory (already here)
- ✅ logs/ directory (already here)

## Quick Start

Once you have all files:

```bash
# 1. Go to this directory
cd ~/Desktop/unsafe-browser-mcp

# 2. Verify files
ls -la
# Should see: Dockerfile, docker-compose.yml, requirements.txt, and 3 .py files

# 3. Build Docker image
docker-compose build

# 4. Test it!
docker-compose run --rm simple-fetcher
```

## Need Help?

Check the full README.md artifact in the chat for complete documentation.
