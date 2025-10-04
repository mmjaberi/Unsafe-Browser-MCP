#!/usr/bin/env python3
"""
HTTP/SSE wrapper for MCP server
Allows web-based LLM clients to connect via HTTP
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Any, Dict, Optional
import asyncio
import json
from datetime import datetime

# Import MCP server components
from mcp_server import get_browser, get_fetcher, cleanup
from mcp_server import app as mcp_app

# FastAPI app
app = FastAPI(
    title="Unsafe Browser MCP HTTP Server",
    description="HTTP/REST API wrapper for MCP browser automation",
    version="2.0.0"
)

# Enable CORS for web clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request models
class ToolCallRequest(BaseModel):
    arguments: Dict[str, Any]

class NavigateRequest(BaseModel):
    url: str

class ClickRequest(BaseModel):
    selector: str

class FillRequest(BaseModel):
    selector: str
    text: str

class ScreenshotRequest(BaseModel):
    filename: Optional[str] = "screenshot.png"
    full_page: Optional[bool] = True

# ============================================================================
# ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    """API information"""
    return {
        "name": "Unsafe Browser MCP Server",
        "version": "2.0.0",
        "protocol": "MCP over HTTP",
        "description": "Browser automation with SSL bypass",
        "endpoints": {
            "info": "GET /",
            "health": "GET /health",
            "tools": "GET /tools",
            "call": "POST /call/{tool_name}",
            "navigate": "POST /api/navigate",
            "click": "POST /api/click",
            "fill": "POST /api/fill",
            "screenshot": "POST /api/screenshot"
        },
        "documentation": "/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "unsafe-browser-mcp"
    }

@app.get("/tools")
async def list_tools():
    """List all available MCP tools"""
    try:
        tools = await mcp_app.list_tools()
        return {
            "tools": [
                {
                    "name": t.name,
                    "description": t.description,
                    "inputSchema": t.inputSchema
                }
                for t in tools
            ],
            "count": len(tools)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/call/{tool_name}")
async def call_tool(tool_name: str, request: ToolCallRequest):
    """
    Call any MCP tool by name
    
    Example:
    POST /call/browser_navigate
    {"arguments": {"url": "https://example.com"}}
    """
    try:
        result = await mcp_app.call_tool(tool_name, request.arguments)
        
        # Convert TextContent to dict
        response_data = []
        for item in result:
            if hasattr(item, 'text'):
                try:
                    # Try to parse as JSON
                    parsed = json.loads(item.text)
                    response_data.append(parsed)
                except:
                    # Return as plain text
                    response_data.append({"text": item.text})
            elif hasattr(item, 'data'):
                # Image content
                response_data.append({
                    "type": "image",
                    "data": item.data,
                    "mimeType": item.mimeType
                })
        
        return {
            "success": True,
            "tool": tool_name,
            "result": response_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# CONVENIENT API ENDPOINTS
# ============================================================================

@app.post("/api/navigate")
async def navigate(request: NavigateRequest):
    """Navigate to a URL"""
    browser = await get_browser()
    result = await browser.navigate(request.url)
    return result

@app.post("/api/click")
async def click(request: ClickRequest):
    """Click an element"""
    browser = await get_browser()
    result = await browser.smart_click(request.selector)
    return result

@app.post("/api/fill")
async def fill(request: FillRequest):
    """Fill an input field"""
    browser = await get_browser()
    result = await browser.fill(request.selector, request.text)
    return result

@app.post("/api/screenshot")
async def screenshot(request: ScreenshotRequest):
    """Take a screenshot"""
    browser = await get_browser()
    result = await browser.screenshot(request.filename, request.full_page)
    
    if result["success"]:
        # Read and return screenshot as base64
        import base64
        import os
        filepath = os.path.join(browser.screenshot_dir, request.filename)
        try:
            with open(filepath, "rb") as f:
                img_data = base64.b64encode(f.read()).decode()
            return {
                "success": True,
                "filename": request.filename,
                "image": img_data,
                "mimeType": "image/png"
            }
        except:
            return result
    return result

@app.post("/api/fetch")
async def fetch_url(request: Dict[str, str]):
    """Fetch a URL"""
    fetcher = await get_fetcher()
    result = await fetcher.fetch(request["url"])
    
    # Truncate content
    if result.get("success") and "content" in result:
        result["content"] = result["content"][:1000]
        result["content_truncated"] = True
    
    return result

@app.get("/api/sessions")
async def list_sessions():
    """List all saved sessions"""
    browser = await get_browser()
    sessions = browser.session_manager.list_sessions()
    
    session_details = []
    for s in sessions:
        try:
            import os
            session_path = os.path.join(browser.session_manager.session_dir, f"{s}.json")
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
    
    return {"sessions": session_details, "count": len(session_details)}

@app.post("/api/sessions/{name}/save")
async def save_session(name: str):
    """Save current session"""
    browser = await get_browser()
    result = await browser.save_session(name)
    return result

@app.post("/api/sessions/{name}/load")
async def load_session(name: str, auto_navigate: bool = False):
    """Load a session"""
    browser = await get_browser()
    result = await browser.load_session(name, auto_navigate)
    return result

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    await cleanup()

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    print("="*70)
    print("🌐 Starting Unsafe Browser MCP HTTP Server")
    print("="*70)
    print("\n📍 Endpoints:")
    print("  - API Docs: http://localhost:8000/docs")
    print("  - Tools: http://localhost:8000/tools")
    print("  - Health: http://localhost:8000/health")
    print("\n💡 Example:")
    print("  curl http://localhost:8000/tools")
    print("  curl -X POST http://localhost:8000/api/navigate -H 'Content-Type: application/json' -d '{\"url\": \"https://example.com\"}'")
    print("\n⚠️  WARNING: SSL verification disabled")
    print("="*70)
    print()
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
