# Unsafe Browser MCP Server

A Model Context Protocol (MCP) server that provides browser automation with SSL certificate bypass capabilities for testing and development purposes.

## ⚠️ Security Warning

This server **bypasses SSL certificate validation**. It should **ONLY** be used for:
- Development and testing environments
- Internal tools with self-signed certificates
- Legitimate security testing with authorization
- IoT devices with invalid certificates

**DO NOT use this for:**
- Production applications
- Handling sensitive data
- Bypassing security on public websites without authorization

## 🚀 Features

- **Browser Automation**: Full browser control with Playwright
- **SSL Bypass**: Access sites with self-signed, expired, or invalid SSL certificates
- **Batch Fetching**: Concurrent URL fetching (10-15x faster than sequential)
- **Session Management**: Save and restore browser sessions
- **Screenshot Capture**: Take full-page or element screenshots
- **Network Monitoring**: Track network requests and responses
- **Smart Selectors**: Intelligent element detection

## 📋 Requirements

- Docker Desktop (with MCP support)
- Python 3.11+ (for local development)
- macOS, Linux, or Windows with WSL2

## 🛠️ Installation

### Method 1: Docker Desktop (Recommended)

1. **Clone the repository**:
   ```bash
   git clone https://github.com/mmjaberi/Unsafe-Browser-MCP.git
   cd unsafe-browser-mcp
   ```

2. **Build the Docker image**:
   ```bash
   docker build -t unsafe-browser-mcp:latest .
   ```

3. **Add to Docker Desktop MCP Registry**:
   ```bash
   chmod +x add-to-registry-yaml.sh
   ./add-to-registry-yaml.sh
   ```

4. **Restart Docker Desktop**

5. **Enable in Docker Desktop**:
   - Go to Settings → MCP Servers
   - Find "Unsafe Browser MCP"
   - Click Enable

### Method 2: Docker Compose

```bash
docker-compose up -d
```

## 📚 Available Tools

### Browser Automation
- `browser_navigate` - Navigate to URLs with SSL bypass
- `browser_click` - Click elements on pages
- `browser_fill` - Fill form fields
- `browser_screenshot` - Capture screenshots
- `browser_suggest_selectors` - Get element selectors

### Session Management
- `browser_save_session` - Save browser state
- `browser_load_session` - Restore browser state
- `browser_list_sessions` - List saved sessions

### Network Tools
- `fetch_url` - Fetch single URL with SSL bypass
- `fetch_json` - Fetch and parse JSON
- `download_file` - Download files
- `batch_fetch` - Fetch multiple URLs concurrently
- `browser_network_summary` - Get network activity summary

## 💡 Usage Examples

### Navigate to a site with self-signed certificate:
```python
unsafe-browser:browser_navigate("https://self-signed.badssl.com")
```

### Take a screenshot:
```python
unsafe-browser:browser_screenshot("my-screenshot.png", full_page=True)
```

### Batch fetch multiple URLs:
```python
unsafe-browser:batch_fetch([
    "https://example.com",
    "https://another-site.com",
    "https://third-site.com"
])
```

### Fetch URL with SSL bypass:
```python
unsafe-browser:fetch_url("https://expired.badssl.com")
```

## 📂 Directory Structure

```
unsafe-browser-mcp/
├── mcp_server.py              # Main MCP server
├── unsafe_browser_mcp.py      # Browser automation logic
├── Dockerfile                 # Docker image definition
├── docker-compose.yml         # Docker Compose configuration
├── requirements.txt           # Python dependencies
├── downloads/                 # Downloaded files
├── screenshots/               # Captured screenshots
├── logs/                      # Server logs
└── sessions/                  # Saved browser sessions
```

## 🔧 Configuration

The server uses the following volume mappings:
- `./downloads` → `/app/downloads`
- `./screenshots` → `/app/screenshots`
- `./logs` → `/app/logs`
- `./sessions` → `/app/sessions`

## 🧪 Testing

Test with SSL certificate issues:

```bash
# Self-signed certificate
curl https://self-signed.badssl.com

# Expired certificate
curl https://expired.badssl.com

# Wrong hostname
curl https://wrong.host.badssl.com
```

## 📝 License

MIT License - See LICENSE file for details

## 👤 Author

Mohamed AlJaberi

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## ⚖️ Legal Disclaimer

This tool is provided for legitimate testing and development purposes only. Users are responsible for ensuring they have proper authorization before testing any systems. The authors assume no liability for misuse of this software.

## 📞 Support

For issues, questions, or contributions, please open an issue on GitHub.

---

**Remember**: With great power comes great responsibility. Use this tool ethically and legally! 🛡️
