#!/usr/bin/env python3
"""
LM Studio Bridge for Unsafe Browser MCP
Connects LM Studio to browser automation tools
"""

import requests
import json
import sys

# Configuration
LM_STUDIO_URL = "http://localhost:1234/v1/chat/completions"
MCP_URL = "http://localhost:8000"

# Tool definitions for LM Studio (OpenAI format)
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "browser_navigate",
            "description": "Navigate to a URL in the browser. Returns page title and status.",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "The URL to navigate to (e.g., https://example.com)"
                    }
                },
                "required": ["url"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "browser_screenshot",
            "description": "Take a screenshot of the current page. Returns base64 image data.",
            "parameters": {
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
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "browser_click",
            "description": "Click an element on the page. Supports CSS selectors or smart keywords.",
            "parameters": {
                "type": "object",
                "properties": {
                    "selector": {
                        "type": "string",
                        "description": "CSS selector or keyword (e.g., 'login_button', '#submit-btn')"
                    }
                },
                "required": ["selector"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "browser_fill",
            "description": "Fill an input field with text",
            "parameters": {
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
        }
    },
    {
        "type": "function",
        "function": {
            "name": "browser_save_session",
            "description": "Save current browser session (cookies and URL) for later use",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Name for the session (default: default)"
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "browser_load_session",
            "description": "Load a previously saved browser session",
            "parameters": {
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
        }
    }
]


def execute_tool(tool_name, arguments):
    """Execute MCP tool via HTTP"""
    try:
        response = requests.post(
            f"{MCP_URL}/call/{tool_name}",
            json={"arguments": arguments},
            timeout=30
        )
        return response.json()
    except Exception as e:
        return {"success": False, "error": str(e)}


def chat_with_browser(user_message, model="local-model", verbose=True):
    """
    Chat with LM Studio with browser automation tools
    
    Args:
        user_message: The user's message/prompt
        model: LM Studio model name (default: "local-model")
        verbose: Print debug information
    
    Returns:
        Tool result or assistant's response
    """
    
    if verbose:
        print(f"\n💬 User: {user_message}")
    
    messages = [{"role": "user", "content": user_message}]
    
    try:
        # Call LM Studio with tools
        response = requests.post(
            LM_STUDIO_URL,
            json={
                "model": model,
                "messages": messages,
                "tools": TOOLS,
                "tool_choice": "auto",
                "temperature": 0.7,
                "max_tokens": 2000
            },
            timeout=60
        )
        
        if response.status_code != 200:
            return {"error": f"LM Studio error: {response.status_code}", "details": response.text}
        
        result = response.json()
        assistant_message = result["choices"][0]["message"]
        
        # Check if LM wants to call a tool
        if assistant_message.get("tool_calls"):
            results = []
            
            for tool_call in assistant_message["tool_calls"]:
                function_name = tool_call["function"]["name"]
                arguments = json.loads(tool_call["function"]["arguments"])
                
                if verbose:
                    print(f"\n🔧 Calling tool: {function_name}")
                    print(f"📋 Arguments: {json.dumps(arguments, indent=2)}")
                
                # Execute tool via MCP
                tool_result = execute_tool(function_name, arguments)
                
                if verbose:
                    print(f"✅ Result: {json.dumps(tool_result, indent=2)[:200]}...")
                
                results.append({
                    "tool": function_name,
                    "arguments": arguments,
                    "result": tool_result
                })
            
            return results if len(results) > 1 else results[0]
        
        # No tool call, return assistant's text response
        return {"type": "text", "content": assistant_message.get("content", "")}
    
    except Exception as e:
        return {"error": str(e)}


def interactive_mode():
    """Interactive chat mode"""
    print("="*70)
    print("🤖 LM Studio + Browser Automation")
    print("="*70)
    print("\nType your requests or 'quit' to exit")
    print("Examples:")
    print("  - Navigate to example.com and take a screenshot")
    print("  - Go to github.com/login and fill username with 'test'")
    print("  - Save the current session as 'my_session'")
    print("="*70)
    
    while True:
        try:
            user_input = input("\n You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Goodbye!")
                break
            
            if not user_input:
                continue
            
            result = chat_with_browser(user_input)
            
            if isinstance(result, dict) and result.get("type") == "text":
                print(f"\n🤖 Assistant: {result['content']}")
            else:
                print(f"\n🤖 Assistant executed tools successfully!")
        
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")


def main():
    """Main entry point"""
    
    # Check if MCP server is running
    try:
        response = requests.get(f"{MCP_URL}/health", timeout=2)
        print("✅ MCP Server is running")
    except:
        print("❌ MCP Server is not running!")
        print(f"   Start it with: python mcp_server_http.py")
        sys.exit(1)
    
    # Check if LM Studio is running
    try:
        response = requests.get(f"{LM_STUDIO_URL.replace('/v1/chat/completions', '/v1/models')}", timeout=2)
        print("✅ LM Studio is running")
    except:
        print("❌ LM Studio is not running!")
        print("   Start LM Studio and enable the local server")
        sys.exit(1)
    
    print()
    
    # Check for command line argument
    if len(sys.argv) > 1:
        # Single command mode
        user_message = " ".join(sys.argv[1:])
        result = chat_with_browser(user_message)
        print(json.dumps(result, indent=2))
    else:
        # Interactive mode
        interactive_mode()


if __name__ == "__main__":
    main()
