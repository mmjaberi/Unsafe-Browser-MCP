#!/usr/bin/env python3
"""
Full-Featured Unsafe Browser MCP Server
Complete browser automation with click, fill, wait, and more!
"""

import asyncio
import json
import ssl
import os
from typing import Any, Optional
from playwright.async_api import async_playwright, Browser, Page

class FullFeaturedBrowser:
    """Complete browser automation with SSL bypass"""
    
    def __init__(self):
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.playwright = None
        self.screenshot_dir = "/app/screenshots"
        self.download_dir = "/app/downloads"
        
    async def initialize(self):
        """Initialize Playwright browser"""
        self.playwright = await async_playwright().start()
        
        self.browser = await self.playwright.chromium.launch(
            headless=True,
            args=[
                '--ignore-certificate-errors',
                '--ignore-certificate-errors-spki-list',
                '--disable-web-security',
                '--disable-features=IsolateOrigins,site-per-process'
            ]
        )
        
        context = await self.browser.new_context(
            ignore_https_errors=True,
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            viewport={'width': 1920, 'height': 1080}
        )
        
        self.page = await context.new_page()
        print("✅ Full-featured browser initialized (SSL verification disabled)")
    
    async def navigate(self, url: str, timeout: int = 30000) -> dict:
        """Navigate to URL"""
        if not self.page:
            await self.initialize()
        
        try:
            print(f"🌐 Navigating to: {url}")
            response = await self.page.goto(url, wait_until='domcontentloaded', timeout=timeout)
            
            title = await self.page.title()
            url_final = self.page.url
            
            return {
                "success": True,
                "url": url_final,
                "title": title,
                "status": response.status if response else None
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def click(self, selector: str) -> dict:
        """Click an element"""
        if not self.page:
            return {"success": False, "error": "No page loaded. Navigate first."}
        
        try:
            await self.page.click(selector, timeout=10000)
            return {"success": True, "message": f"✅ Clicked: {selector}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def fill(self, selector: str, value: str) -> dict:
        """Fill an input field"""
        if not self.page:
            return {"success": False, "error": "No page loaded. Navigate first."}
        
        try:
            await self.page.fill(selector, value, timeout=10000)
            return {"success": True, "message": f"✅ Filled: {selector}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def type_text(self, selector: str, text: str, delay: int = 100) -> dict:
        """Type text with delay (simulates human typing)"""
        if not self.page:
            return {"success": False, "error": "No page loaded. Navigate first."}
        
        try:
            await self.page.type(selector, text, delay=delay)
            return {"success": True, "message": f"✅ Typed into: {selector}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def press_key(self, key: str) -> dict:
        """Press a keyboard key (Enter, Tab, Escape, etc.)"""
        if not self.page:
            return {"success": False, "error": "No page loaded. Navigate first."}
        
        try:
            await self.page.keyboard.press(key)
            return {"success": True, "message": f"✅ Pressed key: {key}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def wait(self, seconds: float) -> dict:
        """Wait for specified seconds"""
        try:
            await asyncio.sleep(seconds)
            return {"success": True, "message": f"✅ Waited {seconds} seconds"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def wait_for_selector(self, selector: str, timeout: int = 30000) -> dict:
        """Wait for element to appear"""
        if not self.page:
            return {"success": False, "error": "No page loaded. Navigate first."}
        
        try:
            await self.page.wait_for_selector(selector, timeout=timeout)
            return {"success": True, "message": f"✅ Element found: {selector}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def screenshot(self, filename: str = "screenshot.png") -> dict:
        """Take screenshot"""
        if not self.page:
            return {"success": False, "error": "No page loaded. Navigate first."}
        
        try:
            if not filename.startswith('/'):
                filepath = os.path.join(self.screenshot_dir, filename)
            else:
                filepath = filename
                
            await self.page.screenshot(path=filepath, full_page=True)
            return {"success": True, "message": f"✅ Screenshot saved: screenshots/{filename}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def get_text(self, selector: str = "body") -> dict:
        """Get text content of element or whole page"""
        if not self.page:
            return {"success": False, "error": "No page loaded. Navigate first."}
        
        try:
            text = await self.page.inner_text(selector)
            return {"success": True, "text": text, "length": len(text)}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def get_value(self, selector: str) -> dict:
        """Get value of an input field"""
        if not self.page:
            return {"success": False, "error": "No page loaded. Navigate first."}
        
        try:
            value = await self.page.input_value(selector)
            return {"success": True, "value": value}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def select_option(self, selector: str, value: str) -> dict:
        """Select option from dropdown"""
        if not self.page:
            return {"success": False, "error": "No page loaded. Navigate first."}
        
        try:
            await self.page.select_option(selector, value)
            return {"success": True, "message": f"✅ Selected: {value}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def check(self, selector: str) -> dict:
        """Check a checkbox"""
        if not self.page:
            return {"success": False, "error": "No page loaded. Navigate first."}
        
        try:
            await self.page.check(selector)
            return {"success": True, "message": f"✅ Checked: {selector}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def uncheck(self, selector: str) -> dict:
        """Uncheck a checkbox"""
        if not self.page:
            return {"success": False, "error": "No page loaded. Navigate first."}
        
        try:
            await self.page.uncheck(selector)
            return {"success": True, "message": f"✅ Unchecked: {selector}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def hover(self, selector: str) -> dict:
        """Hover over element"""
        if not self.page:
            return {"success": False, "error": "No page loaded. Navigate first."}
        
        try:
            await self.page.hover(selector)
            return {"success": True, "message": f"✅ Hovered: {selector}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def go_back(self) -> dict:
        """Go back in browser history"""
        if not self.page:
            return {"success": False, "error": "No page loaded."}
        
        try:
            await self.page.go_back()
            return {"success": True, "message": "✅ Went back"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def go_forward(self) -> dict:
        """Go forward in browser history"""
        if not self.page:
            return {"success": False, "error": "No page loaded."}
        
        try:
            await self.page.go_forward()
            return {"success": True, "message": "✅ Went forward"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def reload(self) -> dict:
        """Reload current page"""
        if not self.page:
            return {"success": False, "error": "No page loaded."}
        
        try:
            await self.page.reload()
            return {"success": True, "message": "✅ Page reloaded"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def cleanup(self):
        """Close browser"""
        if self.page:
            await self.page.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        print("🧹 Browser cleaned up")


async def main():
    """CLI Interface"""
    browser = FullFeaturedBrowser()
    
    print("="*70)
    print("🔓 FULL-FEATURED UNSAFE BROWSER")
    print("⚠️  WARNING: SSL Certificate Verification DISABLED")
    print("="*70)
    print("\n📍 Navigation:")
    print("  navigate <url>           - Go to URL")
    print("  back                     - Go back")
    print("  forward                  - Go forward")
    print("  reload                   - Reload page")
    print("\n🖱️  Interactions:")
    print("  click <selector>         - Click element")
    print("  fill <selector> <text>   - Fill input field")
    print("  type <selector> <text>   - Type with delay")
    print("  press <key>              - Press key (Enter, Tab, etc.)")
    print("  check <selector>         - Check checkbox")
    print("  uncheck <selector>       - Uncheck checkbox")
    print("  select <selector> <value> - Select dropdown option")
    print("  hover <selector>         - Hover over element")
    print("\n📄 Content:")
    print("  text [selector]          - Get text content")
    print("  value <selector>         - Get input value")
    print("  screenshot [filename]    - Take screenshot")
    print("\n⏱️  Timing:")
    print("  wait <seconds>           - Wait N seconds")
    print("  waitfor <selector>       - Wait for element")
    print("\n🚪 Other:")
    print("  help                     - Show this help")
    print("  quit                     - Exit")
    print("="*70)
    print("\n💡 TIP: Use browser DevTools to find selectors (F12 in browser)")
    print("    Examples: #username, .btn-login, button[type='submit']")
    print("="*70)
    
    try:
        while True:
            command = input("\n> ").strip().split(maxsplit=2)
            
            if not command:
                continue
            
            action = command[0].lower()
            
            if action in ["quit", "exit"]:
                break
            
            elif action == "help":
                print("\nSee commands above ⬆️")
                continue
            
            elif action == "navigate":
                if len(command) < 2:
                    print("❌ Usage: navigate <url>")
                    continue
                result = await browser.navigate(command[1])
                
            elif action == "click":
                if len(command) < 2:
                    print("❌ Usage: click <selector>")
                    continue
                result = await browser.click(command[1])
                
            elif action == "fill":
                if len(command) < 3:
                    print("❌ Usage: fill <selector> <text>")
                    continue
                result = await browser.fill(command[1], command[2])
                
            elif action == "type":
                if len(command) < 3:
                    print("❌ Usage: type <selector> <text>")
                    continue
                result = await browser.type_text(command[1], command[2])
                
            elif action == "press":
                if len(command) < 2:
                    print("❌ Usage: press <key>  (e.g., Enter, Tab, Escape)")
                    continue
                result = await browser.press_key(command[1])
                
            elif action == "check":
                if len(command) < 2:
                    print("❌ Usage: check <selector>")
                    continue
                result = await browser.check(command[1])
                
            elif action == "uncheck":
                if len(command) < 2:
                    print("❌ Usage: uncheck <selector>")
                    continue
                result = await browser.uncheck(command[1])
                
            elif action == "select":
                if len(command) < 3:
                    print("❌ Usage: select <selector> <value>")
                    continue
                result = await browser.select_option(command[1], command[2])
                
            elif action == "hover":
                if len(command) < 2:
                    print("❌ Usage: hover <selector>")
                    continue
                result = await browser.hover(command[1])
                
            elif action == "wait":
                if len(command) < 2:
                    print("❌ Usage: wait <seconds>")
                    continue
                try:
                    seconds = float(command[1])
                    result = await browser.wait(seconds)
                except ValueError:
                    print("❌ Seconds must be a number")
                    continue
                    
            elif action == "waitfor":
                if len(command) < 2:
                    print("❌ Usage: waitfor <selector>")
                    continue
                result = await browser.wait_for_selector(command[1])
                
            elif action == "text":
                selector = command[1] if len(command) > 1 else "body"
                result = await browser.get_text(selector)
                if result.get("success"):
                    text = result.get("text", "")
                    print(f"\n📝 Text Content ({len(text)} chars):")
                    print(text[:1000])
                    continue
                    
            elif action == "value":
                if len(command) < 2:
                    print("❌ Usage: value <selector>")
                    continue
                result = await browser.get_value(command[1])
                if result.get("success"):
                    print(f"\n📋 Value: {result.get('value')}")
                    continue
                    
            elif action == "screenshot":
                filename = command[1] if len(command) > 1 else "screenshot.png"
                result = await browser.screenshot(filename)
                
            elif action == "back":
                result = await browser.go_back()
                
            elif action == "forward":
                result = await browser.go_forward()
                
            elif action == "reload":
                result = await browser.reload()
                
            else:
                print(f"❌ Unknown command: {action}")
                print("Type 'help' to see available commands")
                continue
            
            # Print result
            if result.get("success"):
                if "message" in result:
                    print(result["message"])
                elif "title" in result:
                    print(f"✅ {result.get('title')} - {result.get('url')}")
            else:
                print(f"❌ Error: {result.get('error')}")
    
    except KeyboardInterrupt:
        print("\n\nExiting...")
    finally:
        await browser.cleanup()


if __name__ == "__main__":
    print("\n🚀 Starting Full-Featured Unsafe Browser...\n")
    asyncio.run(main())
