#!/usr/bin/env python3
"""
Ollama Bridge for Unsafe Browser MCP
Connects Ollama to browser automation tools
"""

import requests
import json
import sys

# Configuration
OLLAMA_URL = "http://localhost:11434/api/chat"
MCP_URL = "http://localhost:8000"

# Tool definitions for Ollama
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "browser_navigate",
            "description": "Navigate to a URL in the browser",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "URL to navigate to"}
                },
                "required": ["url"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "browser_screenshot",
            "description": "Take a screenshot of current page",
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {"type": "string", "description": "Screenshot filename"}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "browser_click",
            "description": "Click an element",
            "parameters": {
                "type": "object",
                "properties": {
                    "selector": {"type": "string", "description": "CSS selector"}
                },
                "required": ["selector"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "browser_fill",
            "description": "Fill an input field",
            "parameters": {
                "type": "object",
                "properties": {
                    "selector": {"type": "string"},
                    "text": {"type": "string"}
                },
                "required": ["selector", "text"]
            }
        }
    }
]


def execute_tool(tool_name, arguments):
    """Execute MCP tool"""
    try:
        response = requests.post(
            f"{MCP_URL}/call/{tool_name}",
            json={"arguments": arguments},
            timeout=30
        )
        return response.json()
    except Exception as e:
        return {"success": False, "error": str(e)}


def chat_with_browser(prompt, model="mistral", verbose=True):
    """
    Chat with Ollama using browser tools
    
    Args:
        prompt: User's message
        model: Ollama model (mistral, llama3.1, etc.)
        verbose: Print debug info
    
    Returns:
        Tool result or text response
    """
    
    if verbose:
        print(f"\n💬 User: {prompt}")
        print(f"🤖 Model: {model}")
    
    try:
        # Call Ollama
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "tools": TOOLS,
                "stream": False
            },
            timeout=120
        )
        
        if response.status_code != 200:
            return {"error": f"Ollama error: {response.status_code}"}
        
        result = response.json()
        message = result["message"]
        
        # Check for tool calls
        if "tool_calls" in message:
            results = []
            
            for tool_call in message["tool_calls"]:
                function = tool_call["function"]
                function_name = function["name"]
                arguments = function["arguments"]
                
                # Parse arguments if string
                if isinstance(arguments, str):
                    arguments = json.loads(arguments)
                
                if verbose:
                    print(f"\n🔧 Calling: {function_name}")
                    print(f"📋 Args: {json.dumps(arguments, indent=2)}")
                
                # Execute via MCP
                tool_result = execute_tool(function_name, arguments)
                
                if verbose:
                    print(f"✅ Result: {json.dumps(tool_result, indent=2)[:200]}...")
                
                results.append({
                    "tool": function_name,
                    "arguments": arguments,
                    "result": tool_result
                })
            
            return results if len(results) > 1 else results[0]
        
        # No tool call
        return {"type": "text", "content": message.get("content", "")}
    
    except Exception as e:
        return {"error": str(e)}


def interactive_mode(model="mistral"):
    """Interactive chat"""
    print("="*70)
    print(f"🤖 Ollama ({model}) + Browser Automation")
    print("="*70)
    print("\nType your requests or 'quit' to exit")
    print("Commands:")
    print("  /model <name> - Switch model (mistral, llama3.1, etc.)")
    print("  /quit - Exit")
    print("="*70)
    
    current_model = model
    
    while True:
        try:
            user_input = input("\nYou: ").strip()
            
            if user_input.lower() in ['/quit', 'quit', 'exit', 'q']:
                print("\n👋 Goodbye!")
                break
            
            if user_input.startswith('/model '):
                current_model = user_input.split(' ', 1)[1]
                print(f"✅ Switched to model: {current_model}")
                continue
            
            if not user_input:
                continue
            
            result = chat_with_browser(user_input, model=current_model)
            
            if isinstance(result, dict) and result.get("type") == "text":
                print(f"\n🤖 {current_model}: {result['content']}")
            else:
                print(f"\n🤖 {current_model} executed tools successfully!")
        
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")


def main():
    """Main entry point"""
    
    # Check MCP server
    try:
        requests.get(f"{MCP_URL}/health", timeout=2)
        print("✅ MCP Server is running")
    except:
        print("❌ MCP Server is not running!")
        print("   Start it with: python mcp_server_http.py")
        sys.exit(1)
    
    # Check Ollama
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        models = response.json().get("models", [])
        print(f"✅ Ollama is running ({len(models)} models available)")
        if models:
            print(f"   Available models: {', '.join([m['name'] for m in models[:5]])}")
    except:
        print("❌ Ollama is not running!")
        print("   Start it with: ollama serve")
        sys.exit(1)
    
    print()
    
    # Command line or interactive
    if len(sys.argv) > 1:
        if sys.argv[1] == '-m' and len(sys.argv) > 3:
            # Model specified: python ollama_bridge.py -m llama3.1 "your prompt"
            model = sys.argv[2]
            prompt = " ".join(sys.argv[3:])
            result = chat_with_browser(prompt, model=model)
            print(json.dumps(result, indent=2))
        else:
            # Just prompt: python ollama_bridge.py "your prompt"
            prompt = " ".join(sys.argv[1:])
            result = chat_with_browser(prompt)
            print(json.dumps(result, indent=2))
    else:
        # Interactive mode
        interactive_mode()


if __name__ == "__main__":
    main()
