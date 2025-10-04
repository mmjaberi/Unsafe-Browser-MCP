# Unsafe Browser MCP - Docker Catalog Installation

## Quick Install

```bash
cd ~/unsafe-browser-mcp

# Make script executable
chmod +x install-to-docker-mcp.sh

# Run installation
./install-to-docker-mcp.sh

# Restart LLM
```

## What Gets Installed

The script will:
1. ✅ Build the Docker image
2. ✅ Create catalog entry in `~/.docker/mcp/catalogs/unsafe-browser-mcp/`
3. ✅ Configure LLM.
4. ✅ Create symlink for easy updates

## Directory Structure

```
~/.docker/mcp/catalogs/
└── unsafe-browser-mcp/
    ├── catalog.json          # MCP catalog metadata
    └── source/               # Symlink to project directory
```

## Catalog Location

Your MCP will be installed at:
```
~/.docker/mcp/catalogs/unsafe-browser-mcp/
```

## Managing the Catalog

### View Catalog Info
```bash
cat ~/.docker/mcp/catalogs/unsafe-browser-mcp/catalog.json | jq .
```

### List All Catalogs
```bash
ls -la ~/.docker/mcp/catalogs/
```

### Update the MCP
```bash
cd ~/unsafe-browser-mcp
docker build -t unsafe-browser-mcp:latest .
```

### Uninstall
```bash
rm -rf ~/.docker/mcp/catalogs/unsafe-browser-mcp
```

## Advantages of Docker MCP Catalogs

1. **Organization** - All MCPs in one place
2. **Discovery** - Easy to see what's installed
3. **Metadata** - Rich catalog information
4. **Updates** - Symlink makes updates easier
5. **Sharing** - Catalog can be shared with others

## Catalog Structure

The `catalog.json` includes:
- MCP name and version
- Tool descriptions
- Capabilities list
- Volume mounts
- Environment variables
- Security warnings

## Testing

After installation, ask LLM:

```
"What browser tools do you have available?"
```

```
"Navigate to https://example.com and take a screenshot"
```

## Troubleshooting

### Installation fails
```bash
# Check Python is available
python3 --version

# Check jq is installed (for viewing catalog)
brew install jq  # macOS
```

### Catalog not showing
```bash
# Verify installation
ls -la ~/.docker/mcp/catalogs/unsafe-browser-mcp/

# Check symlink
ls -la ~/.docker/mcp/catalogs/unsafe-browser-mcp/source
```

### Tools not available in LLM
1. Restart Your LLM completely
2. Check Docker is running
3. Verify config: `cat ~/Library/Application\ Support/LLM/LLM_config.json`

## Notes

- The catalog uses symlinks to your project directory
- Updates to the code require rebuilding the Docker image
- The catalog.json file uses `${PROJECT_DIR}` which is replaced during installation
- All sessions, screenshots, and logs are stored in your project directory

## More Info

See the main README.md for full documentation on using the browser tools.
