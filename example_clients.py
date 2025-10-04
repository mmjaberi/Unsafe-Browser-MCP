#!/usr/bin/env python3
"""
Example clients for Universal MCP Server
Shows how to connect from different LLM clients
"""

import asyncio
import requests
import json

# ============================================================================
# EXAMPLE 1: HTTP/REST CLIENT (Any Language)
# ============================================================================

class HTTPClient:
    """Simple HTTP client for any programming language"""
    
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
    
    def list_tools(self):
        """List available tools"""
        response = requests.get(f"{self.base_url}/tools")
        return response.json()
    
    def navigate(self, url):
        """Navigate to URL"""
        response = requests.post(
            f"{self.base_url}/api/navigate",
            json={"url": url}
        )
        return response.json()
    
    def screenshot(self, filename="test.png"):
        """Take screenshot"""
        response = requests.post(
            f"{self.base_url}/api/screenshot",
            json={"filename": filename}
        )
        return response.json()
    
    def call_tool(self, tool_name, arguments):
        """Call any tool"""
        response = requests.post(
            f"{self.base_url}/call/{tool_name}",
            json={"arguments": arguments}
        )
        return response.json()


# ============================================================================
# EXAMPLE 2: PYTHON MCP CLIENT
# ============================================================================

async def mcp_client_example():
    """Direct MCP client using stdio"""
    from mcp.client import Client
    
    async with Client(
        "docker",
        [
            "run", "--rm", "-i",
            "-v", "/Users/mohammedaljaberi/Desktop/unsafe-browser-mcp/downloads:/app/downloads",
            "-v", "/Users/mohammedaljaberi/Desktop/unsafe-browser-mcp/screenshots:/app/screenshots",
            "unsafe-browser-mcp:latest",
            "python", "mcp_server.py"
        ]
    ) as client:
        
        # List tools
        tools = await client.list_tools()
        print(f"Available tools: {[t.name for t in tools]}")
        
        # Navigate
        result = await client.call_tool(
            "browser_navigate",
            {"url": "https://example.com"}
        )
        print(f"Navigate result: {result}")
        
        # Screenshot
        screenshot = await client.call_tool(
            "browser_screenshot",
            {"filename": "example.png"}
        )
        print(f"Screenshot: {screenshot}")


# ============================================================================
# EXAMPLE 3: LANGCHAIN INTEGRATION
# ============================================================================

def create_langchain_tools():
    """Create LangChain tools from MCP server"""
    from langchain.tools import Tool
    
    client = HTTPClient()
    
    tools = []
    
    # Navigate tool
    tools.append(Tool(
        name="browser_navigate",
        description="Navigate to a URL in the browser",
        func=lambda url: client.navigate(url)
    ))
    
    # Screenshot tool
    tools.append(Tool(
        name="browser_screenshot",
        description="Take a screenshot of the current page",
        func=lambda filename="screenshot.png": client.screenshot(filename)
    ))
    
    # Add more tools as needed...
    
    return tools


# ============================================================================
# EXAMPLE 4: OPENAI FUNCTION CALLING
# ============================================================================

def get_openai_functions():
    """Get function definitions for OpenAI function calling"""
    return [
        {
            "name": "browser_navigate",
            "description": "Navigate to a URL in the browser",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "The URL to navigate to"
                    }
                },
                "required": ["url"]
            }
        },
        {
            "name": "browser_screenshot",
            "description": "Take a screenshot of the current page",
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": "Filename for screenshot"
                    }
                }
            }
        }
    ]

def execute_function(function_name, arguments):
    """Execute function called by OpenAI"""
    client = HTTPClient()
    return client.call_tool(function_name, arguments)


# ============================================================================
# EXAMPLE 5: CURL COMMANDS (Terminal)
# ============================================================================

def print_curl_examples():
    """Print curl command examples"""
    print("""
# List all tools
curl http://localhost:8000/tools

# Navigate to URL
curl -X POST http://localhost:8000/api/navigate \\
  -H 'Content-Type: application/json' \\
  -d '{"url": "https://example.com"}'

# Take screenshot
curl -X POST http://localhost:8000/api/screenshot \\
  -H 'Content-Type: application/json' \\
  -d '{"filename": "test.png"}'

# Click element
curl -X POST http://localhost:8000/api/click \\
  -H 'Content-Type: application/json' \\
  -d '{"selector": "#login-button"}'

# Fill form field
curl -X POST http://localhost:8000/api/fill \\
  -H 'Content-Type: application/json' \\
  -d '{"selector": "#username", "text": "admin"}'

# List sessions
curl http://localhost:8000/api/sessions

# Save session
curl -X POST http://localhost:8000/api/sessions/my_session/save

# Load session
curl -X POST http://localhost:8000/api/sessions/my_session/load
    """)


# ============================================================================
# EXAMPLE 6: JAVASCRIPT/NODE.JS CLIENT
# ============================================================================

def print_javascript_example():
    """Print JavaScript client example"""
    print("""
// JavaScript/Node.js HTTP Client
const axios = require('axios');

const client = {
    baseURL: 'http://localhost:8000',
    
    async listTools() {
        const response = await axios.get(`${this.baseURL}/tools`);
        return response.data;
    },
    
    async navigate(url) {
        const response = await axios.post(`${this.baseURL}/api/navigate`, { url });
        return response.data;
    },
    
    async screenshot(filename = 'test.png') {
        const response = await axios.post(`${this.baseURL}/api/screenshot`, { filename });
        return response.data;
    },
    
    async callTool(toolName, arguments) {
        const response = await axios.post(
            `${this.baseURL}/call/${toolName}`,
            { arguments }
        );
        return response.data;
    }
};

// Usage
(async () => {
    const tools = await client.listTools();
    console.log('Available tools:', tools);
    
    const nav = await client.navigate('https://example.com');
    console.log('Navigation:', nav);
    
    const screenshot = await client.screenshot('example.png');
    console.log('Screenshot:', screenshot);
})();
    """)


# ============================================================================
# MAIN - RUN EXAMPLES
# ============================================================================

def main():
    print("="*70)
    print("🌐 Universal MCP Client Examples")
    print("="*70)
    
    # Start HTTP server first: python mcp_server_http.py
    print("\n⚠️  Make sure HTTP server is running:")
    print("   python mcp_server_http.py")
    print()
    
    choice = input("Choose example (1-6): ")
    
    if choice == "1":
        print("\n📍 HTTP Client Example")
        client = HTTPClient()
        
        print("\n1. Listing tools...")
        tools = client.list_tools()
        print(f"Found {tools['count']} tools")
        
        print("\n2. Navigating to example.com...")
        result = client.navigate("https://example.com")
        print(f"Result: {result}")
        
        print("\n3. Taking screenshot...")
        screenshot = client.screenshot("http_test.png")
        print(f"Screenshot: {screenshot}")
    
    elif choice == "2":
        print("\n📍 MCP Client Example (async)")
        asyncio.run(mcp_client_example())
    
    elif choice == "3":
        print("\n📍 LangChain Integration")
        tools = create_langchain_tools()
        print(f"Created {len(tools)} LangChain tools:")
        for tool in tools:
            print(f"  - {tool.name}: {tool.description}")
    
    elif choice == "4":
        print("\n📍 OpenAI Function Calling")
        functions = get_openai_functions()
        print("Function definitions for OpenAI:")
        print(json.dumps(functions, indent=2))
    
    elif choice == "5":
        print("\n📍 cURL Examples")
        print_curl_examples()
    
    elif choice == "6":
        print("\n📍 JavaScript Client")
        print_javascript_example()
    
    else:
        print("Invalid choice")


if __name__ == "__main__":
    main()
