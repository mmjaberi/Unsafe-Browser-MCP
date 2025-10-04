#!/usr/bin/env python3
"""
MCP Server for Enhanced Unsafe Browser
Allows Claude Desktop to control the browser via Model Context Protocol
"""

import asyncio
import json
import sys
import os
from typing import Any, Dict, List, Optional
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource
import base64

# Import our enhanced browser
from enhanced_browser_mcp import EnhancedBrowser
from enhanced_simple_fetcher import EnhancedAsyncFetcher

# Initialize MCP server
app = Server("unsafe-browser-mcp")

# Global browser instance
browser: Optional[EnhancedBrowser] = None
fetcher: Optional[EnhancedAsyncFetcher] = None


async def get_browser() -> EnhancedBrowser:
    """Get or create browser instance"""
    global browser
    if browser is None:
        browser = EnhancedBrowser()
        await browser.initialize()
    return browser


async def get_fetcher() -> EnhancedAsyncFetcher:
    """Get or create fetcher instance"""
    global fetcher
    if fetcher is None:
        fetcher = EnhancedAsyncFetcher()
        await fetcher.create_session()
    return fetcher


# ============================================================================
# MCP TOOLS REGISTRATION
# ============================================================================

@app.list_tools()
async def list_tools() -> List[Tool]:
    """List all available browser tools"""
    return [
        # Navigation Tools
        Tool(
            name="browser_navigate",
            description="Navigate to a URL in the browser. Returns page title and status.",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "The URL to navigate to"
                    }
                },
                "required": ["url"]
            }
        ),
        
        # Interaction Tools
        Tool(
            name="browser_click",
            description="Click an element on the page. Supports CSS selectors or smart keywords (login_button, username, etc.)",
            inputSchema={
                "type": "object",
                "properties": {
                    "selector": {
                        "type": "string",
                        "description": "CSS selector or smart keyword (e.g., 'login_button', '#submit-btn')"
                    }
                },
                "required": ["selector"]
            }
        ),
        
        Tool(
            name="browser_fill",
            description="Fill an input field with text",
            inputSchema={
                "type": "object",
                "properties": {
                    "selector": {
                        "type": "string",
                        "description": "CSS selector for the input field"
                    },
                    "text": {
                        "type": "string",
                        "description": "Text to fill in the field"
                    }
                },
                "required": ["selector", "text"]
            }
        ),
        
        Tool(
            name="browser_screenshot",
            description="Take a screenshot of the current page",
            inputSchema={
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": "Filename for the screenshot (default: screenshot.png)"
                    },
                    "full_page": {
                        "type": "boolean",
                        "description": "Capture full page or just viewport (default: true)"
                    }
                },
                "required": []
            }
        ),
        
        # Smart Features
        Tool(
            name="browser_suggest_selectors",
            description="Get suggestions for available selectors on the page",
            inputSchema={
                "type": "object",
                "properties": {
                    "element_type": {
                        "type": "string",
                        "description": "Element type to search for (button, input, a, etc.)"
                    }
                },
                "required": ["element_type"]
            }
        ),
        
        # Session Management
        Tool(
            name="browser_save_session",
            description="Save current browser session (cookies, URL) for later use",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Name for the session (default: default)"
                    }
                },
                "required": []
            }
        ),
        
        Tool(
            name="browser_load_session",
            description="Load a previously saved browser session",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Name of the session to load"
                    },
                    "auto_navigate": {
                        "type": "boolean",
                        "description": "Automatically navigate to saved URL (default: false)"
                    }
                },
                "required": ["name"]
            }
        ),
        
        Tool(
            name="browser_list_sessions",
            description="List all saved browser sessions",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        
        # Network Tools
        Tool(
            name="browser_network_summary",
            description="Get summary of network activity (requests/responses)",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        
        # Fetcher Tools
        Tool(
            name="fetch_url",
            description="Fetch a URL with SSL bypass and retry logic. Returns content and metadata.",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "URL to fetch"
                    }
                },
                "required": ["url"]
            }
        ),
        
        Tool(
            name="fetch_json",
            description="Fetch and parse JSON from a URL",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "URL to fetch JSON from"
                    }
                },
                "required": ["url"]
            }
        ),
        
        Tool(
            name="download_file",
            description="Download a file from URL",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "URL to download from"
                    },
                    "filename": {
                        "type": "string",
                        "description": "Filename to save as"
                    }
                },
                "required": ["url", "filename"]
            }
        ),
        
        Tool(
            name="batch_fetch",
            description="Fetch multiple URLs concurrently (10-15x faster)",
            inputSchema={
                "type": "object",
                "properties": {
                    "urls": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of URLs to fetch"
                    }
                },
                "required": ["urls"]
            }
        ),
    ]


# ============================================================================
# TOOL CALL HANDLERS
# ============================================================================

@app.call_tool()
async def call_tool(name: str, arguments: Any) -> List[TextContent | ImageContent | EmbeddedResource]:
    """Handle tool calls from Claude"""
    
    try:
        # Browser Navigation
        if name == "browser_navigate":
            b = await get_browser()
            result = await b.navigate(arguments["url"])
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
        
        # Browser Click
        elif name == "browser_click":
            b = await get_browser()
            result = await b.smart_click(arguments["selector"])
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
        
        # Browser Fill
        elif name == "browser_fill":
            b = await get_browser()
            result = await b.fill(arguments["selector"], arguments["text"])
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
        
        # Browser Screenshot
        elif name == "browser_screenshot":
            b = await get_browser()
            filename = arguments.get("filename", "screenshot.png")
            full_page = arguments.get("full_page", True)
            
            result = await b.screenshot(filename, full_page)
            
            if result["success"]:
                # Read screenshot and return as base64
                try:
                    filepath = os.path.join(b.screenshot_dir, filename)
                    with open(filepath, "rb") as f:
                        img_data = base64.b64encode(f.read()).decode()
                    
                    return [
                        TextContent(
                            type="text",
                            text=f"Screenshot saved: {filename}"
                        ),
                        ImageContent(
                            type="image",
                            data=img_data,
                            mimeType="image/png"
                        )
                    ]
                except Exception as e:
                    return [TextContent(
                        type="text",
                        text=f"Screenshot saved but couldn't read: {e}"
                    )]
            else:
                return [TextContent(
                    type="text",
                    text=json.dumps(result, indent=2)
                )]
        
        # Suggest Selectors
        elif name == "browser_suggest_selectors":
            b = await get_browser()
            result = await b.suggest_selectors(arguments["element_type"])
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
        
        # Save Session
        elif name == "browser_save_session":
            b = await get_browser()
            name_arg = arguments.get("name", "default")
            result = await b.save_session(name_arg)
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
        
        # Load Session
        elif name == "browser_load_session":
            b = await get_browser()
            name_arg = arguments["name"]
            auto_nav = arguments.get("auto_navigate", False)
            result = await b.load_session(name_arg, auto_nav)
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
        
        # List Sessions
        elif name == "browser_list_sessions":
            b = await get_browser()
            sessions = b.session_manager.list_sessions()
            
            # Get session details
            session_details = []
            for s in sessions:
                try:
                    session_path = os.path.join(b.session_manager.session_dir, f"{s}.json")
                    with open(session_path, 'r') as f:
                        data = json.load(f)
                    session_details.append({
                        "name": s,
                        "cookie_count": data.get("cookie_count", 0),
                        "url": data.get("current_url", "N/A"),
                        "saved_at": data.get("saved_at", "N/A")
                    })
                except:
                    session_details.append({"name": s})
            
            return [TextContent(
                type="text",
                text=json.dumps({"sessions": session_details}, indent=2)
            )]
        
        # Network Summary
        elif name == "browser_network_summary":
            b = await get_browser()
            result = await b.get_network_summary()
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
        
        # Fetch URL
        elif name == "fetch_url":
            f = await get_fetcher()
            result = await f.fetch(arguments["url"])
            
            # Truncate content for display
            if result.get("success") and "content" in result:
                content_preview = result["content"][:1000]
                result["content"] = content_preview
                result["content_truncated"] = True
            
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
        
        # Fetch JSON
        elif name == "fetch_json":
            f = await get_fetcher()
            result = await f.fetch_json(arguments["url"])
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
        
        # Download File
        elif name == "download_file":
            f = await get_fetcher()
            result = await f.download_file(
                arguments["url"],
                arguments["filename"],
                show_progress=False
            )
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
        
        # Batch Fetch
        elif name == "batch_fetch":
            f = await get_fetcher()
            results = await f.batch_fetch(arguments["urls"])
            
            # Truncate content
            for r in results:
                if r.get("success") and "content" in r:
                    r["content"] = r["content"][:500]
                    r["content_truncated"] = True
            
            return [TextContent(
                type="text",
                text=json.dumps({"results": results}, indent=2)
            )]
        
        else:
            return [TextContent(
                type="text",
                text=f"Unknown tool: {name}"
            )]
    
    except Exception as e:
        import traceback
        return [TextContent(
            type="text",
            text=f"Error executing {name}: {str(e)}\n{traceback.format_exc()}"
        )]


# ============================================================================
# CLEANUP
# ============================================================================

async def cleanup():
    """Cleanup browser and fetcher instances"""
    global browser, fetcher
    
    if browser:
        await browser.cleanup()
        browser = None
    
    if fetcher:
        await fetcher.close_session()
        fetcher = None


# ============================================================================
# MAIN
# ============================================================================

async def main():
    """Run MCP server"""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    finally:
        asyncio.run(cleanup())
