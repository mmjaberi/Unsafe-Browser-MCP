#!/usr/bin/env python3
"""
Enhanced Full-Featured Unsafe Browser MCP Server
Features: Session manager, network inspector, smart selectors, better logging
"""

import asyncio
import json
import ssl
import os
import logging
from typing import Any, Optional, List, Dict
from playwright.async_api import async_playwright, Browser, Page, BrowserContext
from datetime import datetime
import pickle

# ============================================================================
# LOGGING SETUP
# ============================================================================

def setup_browser_logging():
    """Setup logging for browser operations"""
    os.makedirs("/app/logs", exist_ok=True)
    
    logger = logging.getLogger("browser")
    logger.setLevel(logging.INFO)
    
    # File handler
    fh = logging.FileHandler("/app/logs/browser.log")
    fh.setLevel(logging.DEBUG)
    
    # Console handler
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%H:%M:%S'
    )
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    
    logger.addHandler(fh)
    logger.addHandler(ch)
    
    return logger

logger = setup_browser_logging()


# ============================================================================
# NETWORK INSPECTOR
# ============================================================================

class NetworkInspector:
    """Track and log all network requests"""
    
    def __init__(self):
        self.requests: List[Dict] = []
        self.responses: List[Dict] = []
        self.enabled = True
    
    def log_request(self, request):
        """Log outgoing request"""
        if not self.enabled:
            return
        
        req_data = {
            "timestamp": datetime.now().isoformat(),
            "method": request.method,
            "url": request.url,
            "headers": dict(request.headers),
            "resource_type": request.resource_type
        }
        self.requests.append(req_data)
        logger.debug(f"→ {request.method} {request.url}")
    
    def log_response(self, response):
        """Log incoming response"""
        if not self.enabled:
            return
        
        resp_data = {
            "timestamp": datetime.now().isoformat(),
            "url": response.url,
            "status": response.status,
            "headers": dict(response.headers),
            "ok": response.ok
        }
        self.responses.append(resp_data)
        
        status_icon = "✅" if response.ok else "❌"
        logger.debug(f"← {status_icon} {response.status} {response.url}")
    
    def get_summary(self) -> Dict:
        """Get network activity summary"""
        return {
            "total_requests": len(self.requests),
            "total_responses": len(self.responses),
            "failed_requests": len([r for r in self.responses if not r.get("ok", True)]),
            "requests": self.requests[-10:],  # Last 10
            "responses": self.responses[-10:]  # Last 10
        }
    
    def clear(self):
        """Clear all logged requests/responses"""
        self.requests.clear()
        self.responses.clear()
        logger.info("Network inspector cleared")
    
    def export_har(self, filename: str = "network.har"):
        """Export network activity as HAR file"""
        har_data = {
            "log": {
                "version": "1.2",
                "creator": {"name": "Enhanced Browser MCP", "version": "2.0"},
                "entries": []
            }
        }
        
        for req, resp in zip(self.requests, self.responses):
            entry = {
                "startedDateTime": req["timestamp"],
                "request": {
                    "method": req["method"],
                    "url": req["url"],
                    "headers": [{"name": k, "value": v} for k, v in req["headers"].items()]
                },
                "response": {
                    "status": resp["status"],
                    "headers": [{"name": k, "value": v} for k, v in resp["headers"].items()]
                }
            }
            har_data["log"]["entries"].append(entry)
        
        filepath = f"/app/logs/{filename}"
        with open(filepath, 'w') as f:
            json.dump(har_data, f, indent=2)
        
        logger.info(f"HAR file exported: {filepath}")
        return filepath


# ============================================================================
# SESSION MANAGER
# ============================================================================

class SessionManager:
    """Save and restore browser sessions"""
    
    def __init__(self, session_dir: str = "/app/sessions"):
        self.session_dir = session_dir
        os.makedirs(session_dir, exist_ok=True)
    
    async def save_session(self, context: BrowserContext, name: str = "default", current_url: str = None) -> str:
        """Save browser session (cookies, storage)"""
        session_path = os.path.join(self.session_dir, f"{name}.json")
        
        # Get cookies
        cookies = await context.cookies()
        
        # Get cookie domains for info
        domains = list(set([c.get('domain', 'unknown') for c in cookies]))
        
        # Save session data
        session_data = {
            "saved_at": datetime.now().isoformat(),
            "cookies": cookies,
            "cookie_count": len(cookies),
            "domains": domains,
            "current_url": current_url,
            "name": name
        }
        
        with open(session_path, 'w') as f:
            json.dump(session_data, f, indent=2)
        
        logger.info(f"Session saved: {name} ({len(cookies)} cookies from {len(domains)} domains)")
        return session_path
    
    async def load_session(self, context: BrowserContext, name: str = "default") -> Dict:
        """Load browser session"""
        session_path = os.path.join(self.session_dir, f"{name}.json")
        
        if not os.path.exists(session_path):
            logger.warning(f"Session not found: {name}")
            return {"success": False, "error": "Session not found"}
        
        try:
            with open(session_path, 'r') as f:
                session_data = json.load(f)
            
            # Restore cookies
            await context.add_cookies(session_data["cookies"])
            
            cookie_count = len(session_data['cookies'])
            domains = session_data.get('domains', [])
            saved_url = session_data.get('current_url')
            
            logger.info(f"Session loaded: {name} ({cookie_count} cookies from {len(domains)} domains)")
            
            return {
                "success": True,
                "cookie_count": cookie_count,
                "domains": domains,
                "saved_url": saved_url,
                "saved_at": session_data.get('saved_at')
            }
        except Exception as e:
            logger.error(f"Failed to load session: {e}")
            return {"success": False, "error": str(e)}
    
    def list_sessions(self) -> List[str]:
        """List all saved sessions"""
        sessions = []
        for filename in os.listdir(self.session_dir):
            if filename.endswith('.json'):
                sessions.append(filename[:-5])  # Remove .json
        return sessions
    
    def delete_session(self, name: str) -> bool:
        """Delete a session"""
        session_path = os.path.join(self.session_dir, f"{name}.json")
        if os.path.exists(session_path):
            os.remove(session_path)
            logger.info(f"Session deleted: {name}")
            return True
        return False


# ============================================================================
# SMART SELECTOR HELPER
# ============================================================================

class SmartSelector:
    """Helper for finding and suggesting selectors"""
    
    # Common selector patterns
    COMMON_SELECTORS = {
        "login_button": ["button[type='submit']", ".login-btn", "#login", "button:has-text('Login')"],
        "username": ["input[name='username']", "input[type='email']", "#username", "#email"],
        "password": ["input[name='password']", "input[type='password']", "#password"],
        "search": ["input[type='search']", "input[name='q']", "#search", ".search-input"],
        "submit": ["button[type='submit']", "input[type='submit']", ".submit-btn"],
        "close": ["button.close", ".modal-close", "[aria-label='Close']"],
        "menu": [".menu", "#menu", "nav", ".navigation"],
        "link": ["a", "a[href]"],
        "image": ["img", "img[src]"],
        "form": ["form"],
    }
    
    @staticmethod
    async def find_element(page: Page, keyword: str) -> Optional[str]:
        """Find element using smart keyword matching"""
        
        # Check common patterns
        if keyword in SmartSelector.COMMON_SELECTORS:
            for selector in SmartSelector.COMMON_SELECTORS[keyword]:
                try:
                    element = await page.query_selector(selector)
                    if element:
                        logger.info(f"Found '{keyword}' using selector: {selector}")
                        return selector
                except:
                    continue
        
        # Try text matching
        try:
            selector = f"text={keyword}"
            element = await page.query_selector(selector)
            if element:
                logger.info(f"Found element with text: {keyword}")
                return selector
        except:
            pass
        
        return None
    
    @staticmethod
    async def suggest_selectors(page: Page, element_type: str = "button") -> List[str]:
        """Suggest available selectors for element type"""
        suggestions = []
        
        # Get all elements of type
        elements = await page.query_selector_all(element_type)
        
        for i, elem in enumerate(elements[:10]):  # Limit to 10
            try:
                # Get text content
                text = await elem.inner_text()
                # Get attributes
                id_attr = await elem.get_attribute("id")
                class_attr = await elem.get_attribute("class")
                
                suggestion = {
                    "index": i,
                    "text": text.strip()[:50] if text else None,
                    "id": f"#{id_attr}" if id_attr else None,
                    "class": f".{class_attr.split()[0]}" if class_attr else None
                }
                suggestions.append(suggestion)
            except:
                continue
        
        return suggestions


# ============================================================================
# ENHANCED BROWSER
# ============================================================================

class EnhancedBrowser:
    """Complete browser automation with all enhancements"""
    
    def __init__(self, proxy: Optional[str] = None, headless: bool = True):
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.playwright = None
        self.screenshot_dir = "/app/screenshots"
        self.download_dir = "/app/downloads"
        self.proxy = proxy
        self.headless = headless
        
        # Enhanced features
        self.network_inspector = NetworkInspector()
        self.session_manager = SessionManager()
        self.smart_selector = SmartSelector()
        
        logger.info("Enhanced browser initialized")
    
    async def initialize(self):
        """Initialize Playwright browser with all features"""
        self.playwright = await async_playwright().start()
        
        # Browser args
        args = [
            '--ignore-certificate-errors',
            '--ignore-certificate-errors-spki-list',
            '--disable-web-security',
            '--disable-features=IsolateOrigins,site-per-process'
        ]
        
        # Add proxy if specified
        if self.proxy:
            args.append(f'--proxy-server={self.proxy}')
            logger.info(f"Using proxy: {self.proxy}")
        
        self.browser = await self.playwright.chromium.launch(
            headless=self.headless,
            args=args
        )
        
        # Create context
        context_options = {
            "ignore_https_errors": True,
            "user_agent": 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            "viewport": {'width': 1920, 'height': 1080}
        }
        
        if self.proxy:
            # Proxy auth can be added here if needed
            pass
        
        self.context = await self.browser.new_context(**context_options)
        self.page = await self.context.new_page()
        
        # Setup network monitoring
        self.page.on("request", self.network_inspector.log_request)
        self.page.on("response", self.network_inspector.log_response)
        
        logger.info("✅ Enhanced browser ready (SSL verification disabled)")
    
    async def navigate(self, url: str, timeout: int = 30000) -> dict:
        """Navigate to URL with enhanced logging"""
        if not self.page:
            await self.initialize()
        
        try:
            logger.info(f"🌐 Navigating to: {url}")
            response = await self.page.goto(url, wait_until='domcontentloaded', timeout=timeout)
            
            title = await self.page.title()
            url_final = self.page.url
            
            logger.info(f"✅ Loaded: {title}")
            
            return {
                "success": True,
                "url": url_final,
                "title": title,
                "status": response.status if response else None
            }
        except Exception as e:
            logger.error(f"Navigation failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def smart_click(self, selector_or_keyword: str) -> dict:
        """Click using smart selector or keyword"""
        if not self.page:
            return {"success": False, "error": "No page loaded"}
        
        # Try as regular selector first
        try:
            await self.page.click(selector_or_keyword, timeout=10000)
            logger.info(f"✅ Clicked: {selector_or_keyword}")
            return {"success": True, "message": f"✅ Clicked: {selector_or_keyword}"}
        except:
            pass
        
        # Try smart selector
        smart_selector = await self.smart_selector.find_element(self.page, selector_or_keyword)
        if smart_selector:
            try:
                await self.page.click(smart_selector, timeout=10000)
                logger.info(f"✅ Clicked using smart selector: {smart_selector}")
                return {"success": True, "message": f"✅ Clicked: {selector_or_keyword} (using {smart_selector})"}
            except Exception as e:
                logger.error(f"Smart click failed: {e}")
                return {"success": False, "error": str(e)}
        
        return {"success": False, "error": f"Element not found: {selector_or_keyword}"}
    
    async def fill(self, selector: str, value: str) -> dict:
        """Fill input field with logging"""
        if not self.page:
            return {"success": False, "error": "No page loaded"}
        
        try:
            await self.page.fill(selector, value, timeout=10000)
            logger.info(f"✅ Filled: {selector}")
            return {"success": True, "message": f"✅ Filled: {selector}"}
        except Exception as e:
            logger.error(f"Fill failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def screenshot(self, filename: str = "screenshot.png", full_page: bool = True) -> dict:
        """Take screenshot with annotation support"""
        if not self.page:
            return {"success": False, "error": "No page loaded"}
        
        try:
            if not filename.startswith('/'):
                filepath = os.path.join(self.screenshot_dir, filename)
            else:
                filepath = filename
            
            await self.page.screenshot(path=filepath, full_page=full_page)
            logger.info(f"📸 Screenshot saved: {filename}")
            return {"success": True, "message": f"✅ Screenshot saved: screenshots/{filename}"}
        except Exception as e:
            logger.error(f"Screenshot failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_network_summary(self) -> dict:
        """Get network activity summary"""
        return self.network_inspector.get_summary()
    
    async def export_network_har(self, filename: str = "network.har") -> dict:
        """Export network activity as HAR file"""
        try:
            filepath = self.network_inspector.export_har(filename)
            return {"success": True, "path": filepath}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def save_session(self, name: str = "default") -> dict:
        """Save current browser session"""
        try:
            # Check if browser is initialized
            if not self.context:
                return {"success": False, "error": "No browser session active. Navigate to a page first."}
            
            # Get current URL if page exists
            current_url = self.page.url if self.page else None
            
            path = await self.session_manager.save_session(self.context, name, current_url)
            return {"success": True, "path": path, "message": f"✅ Session saved: {name}"}
        except Exception as e:
            logger.error(f"Save session failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def load_session(self, name: str = "default", auto_navigate: bool = False) -> dict:
        """Load browser session"""
        try:
            # Initialize browser if not already initialized
            if not self.context:
                await self.initialize()
            
            result = await self.session_manager.load_session(self.context, name)
            
            if result["success"]:
                # Build detailed message
                cookie_count = result.get("cookie_count", 0)
                domains = result.get("domains", [])
                saved_url = result.get("saved_url")
                
                message = f"✅ Session loaded: {name}\n"
                message += f"   Cookies: {cookie_count} from {len(domains)} domains\n"
                
                if domains:
                    message += f"   Domains: {', '.join(domains[:3])}"
                    if len(domains) > 3:
                        message += f" +{len(domains)-3} more"
                    message += "\n"
                
                if saved_url:
                    message += f"   Saved URL: {saved_url}\n"
                    message += f"   ⚠️  Navigate to {saved_url} to use the session"
                    
                    # Auto-navigate if requested
                    if auto_navigate and saved_url:
                        logger.info(f"Auto-navigating to: {saved_url}")
                        nav_result = await self.navigate(saved_url)
                        if nav_result["success"]:
                            message += f"\n   ✅ Auto-navigated to {saved_url}"
                        else:
                            message += f"\n   ❌ Failed to auto-navigate: {nav_result.get('error')}"
                
                return {"success": True, "message": message, **result}
            else:
                return result
        except Exception as e:
            logger.error(f"Load session failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def suggest_selectors(self, element_type: str = "button") -> dict:
        """Get selector suggestions for elements"""
        try:
            suggestions = await self.smart_selector.suggest_selectors(self.page, element_type)
            return {"success": True, "suggestions": suggestions}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def cleanup(self):
        """Close browser and save logs"""
        if self.page:
            await self.page.close()
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        logger.info("🧹 Browser cleaned up")


# ============================================================================
# MAIN CLI
# ============================================================================

async def main():
    """Enhanced CLI Interface"""
    browser = EnhancedBrowser()
    
    print("="*70)
    print("🚀 ENHANCED FULL-FEATURED UNSAFE BROWSER")
    print("⚠️  WARNING: SSL Certificate Verification DISABLED")
    print("="*70)
    print("\n📍 Navigation:")
    print("  nav <url>               - Navigate to URL")
    print("\n🖱️  Interactions:")
    print("  click <selector>        - Click element (supports smart selectors)")
    print("  fill <selector> <text>  - Fill input field")
    print("\n📸 Capture:")
    print("  screenshot [name]       - Take screenshot")
    print("\n🔍 Smart Features:")
    print("  suggest <type>          - Suggest selectors (button, input, etc.)")
    print("  network                 - Show network activity summary")
    print("  export-har [name]       - Export network logs as HAR")
    print("\n💾 Session Management:")
    print("  save-session [name]      - Save current session")
    print("  load-session [name] [-n] - Load session (use -n to auto-navigate)")
    print("  list-sessions            - List all sessions with details")
    print("  session-info [name]      - Show detailed session information")
    print("\n📋 Other:")
    print("  logs                    - Show recent logs")
    print("  help                    - Show this help")
    print("  quit                    - Exit")
    print("="*70)
    
    try:
        while True:
            command = input("\n> ").strip().split(maxsplit=2)
            
            if not command:
                continue
            
            action = command[0].lower()
            
            if action in ["quit", "exit"]:
                break
            
            elif action == "nav" or action == "navigate":
                if len(command) < 2:
                    print("❌ Usage: nav <url>")
                    continue
                result = await browser.navigate(command[1])
                if result["success"]:
                    print(f"✅ {result['title']} ({result['status']})")
                else:
                    print(f"❌ {result['error']}")
            
            elif action == "click":
                if len(command) < 2:
                    print("❌ Usage: click <selector>")
                    continue
                result = await browser.smart_click(command[1])
                print(result.get("message") or f"❌ {result.get('error')}")
            
            elif action == "fill":
                if len(command) < 3:
                    print("❌ Usage: fill <selector> <text>")
                    continue
                result = await browser.fill(command[1], command[2])
                print(result.get("message") or f"❌ {result.get('error')}")
            
            elif action == "screenshot":
                filename = command[1] if len(command) > 1 else "screenshot.png"
                result = await browser.screenshot(filename)
                print(result.get("message") or f"❌ {result.get('error')}")
            
            elif action == "suggest":
                elem_type = command[1] if len(command) > 1 else "button"
                result = await browser.suggest_selectors(elem_type)
                if result["success"]:
                    print(f"\n🔍 Found {len(result['suggestions'])} {elem_type} elements:")
                    for s in result['suggestions']:
                        print(f"  [{s['index']}] Text: {s.get('text', 'N/A')}")
                        if s.get('id'):
                            print(f"       ID: {s['id']}")
                        if s.get('class'):
                            print(f"       Class: {s['class']}")
                else:
                    print(f"❌ {result['error']}")
            
            elif action == "network":
                summary = await browser.get_network_summary()
                print(f"\n📊 Network Summary:")
                print(f"  Total Requests: {summary['total_requests']}")
                print(f"  Total Responses: {summary['total_responses']}")
                print(f"  Failed: {summary['failed_requests']}")
                print(f"\n  Recent requests:")
                for req in summary['requests'][-5:]:
                    print(f"    → {req['method']} {req['url']}")
            
            elif action == "export-har":
                filename = command[1] if len(command) > 1 else "network.har"
                result = await browser.export_network_har(filename)
                if result["success"]:
                    print(f"✅ HAR exported: {result['path']}")
                else:
                    print(f"❌ {result['error']}")
            
            elif action == "save-session":
                name = command[1] if len(command) > 1 else "default"
                result = await browser.save_session(name)
                print(result.get("message") or f"❌ {result.get('error')}")
            
            elif action == "load-session":
                parts = command[1].split() if len(command) > 1 else []
                name = parts[0] if parts else "default"
                auto_nav = "--nav" in parts or "-n" in parts
                
                result = await browser.load_session(name, auto_navigate=auto_nav)
                print(result.get("message") or f"❌ {result.get('error')}")
            
            elif action == "list-sessions":
                sessions = browser.session_manager.list_sessions()
                if sessions:
                    print(f"\n💾 Saved sessions ({len(sessions)}):")
                    for s in sessions:
                        # Try to load session info
                        try:
                            session_path = f"/app/sessions/{s}.json"
                            with open(session_path, 'r') as f:
                                data = json.load(f)
                            cookie_count = data.get('cookie_count', 0)
                            saved_url = data.get('current_url', 'N/A')
                            print(f"  - {s} ({cookie_count} cookies) - {saved_url}")
                        except:
                            print(f"  - {s}")
                else:
                    print("No saved sessions")
            
            elif action == "session-info":
                name = command[1] if len(command) > 1 else "default"
                try:
                    session_path = f"/app/sessions/{name}.json"
                    with open(session_path, 'r') as f:
                        data = json.load(f)
                    
                    print(f"\n📊 Session Info: {name}")
                    print(f"  Saved at: {data.get('saved_at', 'N/A')}")
                    print(f"  Cookies: {data.get('cookie_count', 0)}")
                    print(f"  Domains: {', '.join(data.get('domains', []))}")
                    print(f"  URL: {data.get('current_url', 'N/A')}")
                except FileNotFoundError:
                    print(f"❌ Session not found: {name}")
                except Exception as e:
                    print(f"❌ Error: {e}")
            
            elif action == "logs":
                print("\n📋 Recent logs:")
                try:
                    with open("/app/logs/browser.log", "r") as f:
                        lines = f.readlines()
                        for line in lines[-15:]:
                            print(line.strip())
                except:
                    print("No logs yet")
            
            elif action == "help":
                print("\nSee commands above ⬆️")
            
            else:
                print(f"❌ Unknown command: {action}")
    
    except KeyboardInterrupt:
        print("\n\nExiting...")
    finally:
        await browser.cleanup()


if __name__ == "__main__":
    print("\n🚀 Starting Enhanced Browser...\n")
    asyncio.run(main())
