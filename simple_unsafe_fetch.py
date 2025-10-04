#!/usr/bin/env python3
"""
Simple Unsafe HTTPS Fetcher
Fixed paths for Docker volume mounting
"""

import ssl
import urllib.request
import urllib.error
import json
import os
from typing import Dict, Any

class UnsafeHTTPSFetcher:
    """Fetch HTTPS content with certificate verification disabled"""
    
    def __init__(self):
        self.ssl_context = ssl.create_default_context()
        self.ssl_context.check_hostname = False
        self.ssl_context.verify_mode = ssl.CERT_NONE
        self.download_dir = "/app/downloads"
    
    def fetch(self, url: str, headers: Dict[str, str] = None) -> Dict[str, Any]:
        """Fetch URL with SSL verification disabled"""
        try:
            req = urllib.request.Request(url)
            req.add_header('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)')
            
            if headers:
                for key, value in headers.items():
                    req.add_header(key, value)
            
            with urllib.request.urlopen(req, context=self.ssl_context, timeout=30) as response:
                content = response.read()
                
                try:
                    text_content = content.decode('utf-8')
                except UnicodeDecodeError:
                    text_content = content.decode('latin-1', errors='ignore')
                
                return {
                    "success": True,
                    "url": response.url,
                    "status": response.status,
                    "headers": dict(response.headers),
                    "content": text_content,
                    "size": len(content),
                    "certificate": "⚠️ Certificate verification DISABLED"
                }
        
        except urllib.error.HTTPError as e:
            return {
                "success": False,
                "error": f"HTTP Error {e.code}: {e.reason}",
                "url": url
            }
        
        except urllib.error.URLError as e:
            return {
                "success": False,
                "error": f"URL Error: {str(e.reason)}",
                "url": url
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "url": url
            }
    
    def fetch_json(self, url: str, headers: Dict[str, str] = None) -> Dict[str, Any]:
        """Fetch and parse JSON response"""
        result = self.fetch(url, headers)
        
        if result["success"]:
            try:
                result["json"] = json.loads(result["content"])
            except json.JSONDecodeError as e:
                result["json_error"] = str(e)
        
        return result
    
    def download_file(self, url: str, filename: str) -> Dict[str, Any]:
        """Download file from HTTPS with untrusted cert"""
        try:
            # Ensure download goes to proper directory
            if not filename.startswith('/'):
                filepath = os.path.join(self.download_dir, filename)
            else:
                filepath = filename
                
            req = urllib.request.Request(url)
            req.add_header('User-Agent', 'Mozilla/5.0')
            
            with urllib.request.urlopen(req, context=self.ssl_context, timeout=60) as response:
                data = response.read()
                
                with open(filepath, 'wb') as f:
                    f.write(data)
                
                return {
                    "success": True,
                    "url": url,
                    "output_path": filepath,
                    "size": len(data),
                    "message": f"✅ Downloaded {len(data)} bytes! Check: downloads/{filename}"
                }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "url": url
            }


def main():
    """CLI interface"""
    fetcher = UnsafeHTTPSFetcher()
    
    print("="*70)
    print("🔓 UNSAFE HTTPS FETCHER")
    print("⚠️  WARNING: SSL Certificate Verification DISABLED")
    print("="*70)
    print("\nCommands:")
    print("  fetch <url>                - Fetch URL content")
    print("  json <url>                 - Fetch and parse JSON")
    print("  download <url> <filename>  - Download file")
    print("  test                       - Test with bad SSL sites")
    print("  quit                       - Exit")
    print("="*70)
    print("\n💡 TIP: Downloads save to ~/Desktop/unsafe-browser-mcp/downloads/")
    print("="*70)
    
    while True:
        try:
            command = input("\n> ").strip().split(maxsplit=2)
            
            if not command:
                continue
            
            action = command[0].lower()
            
            if action == "quit" or action == "exit":
                break
            
            elif action == "fetch":
                if len(command) < 2:
                    print("❌ Usage: fetch <url>")
                    continue
                    
                url = command[1]
                print(f"\n📡 Fetching {url}...")
                result = fetcher.fetch(url)
                
                if result["success"]:
                    print(f"\n✅ Success!")
                    print(f"🔐 Certificate: {result['certificate']}")
                    print(f"📊 Status: {result['status']}")
                    print(f"📄 Size: {result['size']} bytes")
                    print(f"\n📝 Content Preview:")
                    print(result['content'][:500])
                else:
                    print(f"\n❌ Error: {result['error']}")
            
            elif action == "json":
                if len(command) < 2:
                    print("❌ Usage: json <url>")
                    continue
                    
                url = command[1]
                print(f"\n📡 Fetching JSON from {url}...")
                result = fetcher.fetch_json(url)
                
                if result["success"] and "json" in result:
                    print(f"\n✅ Success!")
                    print(f"📊 Status: {result['status']}")
                    print(f"\n📋 JSON Data:")
                    print(json.dumps(result['json'], indent=2)[:500])
                else:
                    print(f"\n❌ Error: {result.get('error', result.get('json_error'))}")
            
            elif action == "download":
                if len(command) < 3:
                    print("❌ Usage: download <url> <filename>")
                    print("   Example: download https://example.com/file.pdf report.pdf")
                    continue
                    
                url = command[1]
                filename = command[2]
                print(f"\n⬇️  Downloading {url}...")
                result = fetcher.download_file(url, filename)
                
                if result["success"]:
                    print(f"\n{result['message']}")
                else:
                    print(f"\n❌ Error: {result['error']}")
            
            elif action == "test":
                print("\n🧪 Testing with known bad SSL certificates...\n")
                
                test_sites = [
                    ("Self-signed", "https://self-signed.badssl.com/"),
                    ("Expired", "https://expired.badssl.com/"),
                    ("Wrong Host", "https://wrong.host.badssl.com/"),
                ]
                
                for name, url in test_sites:
                    print(f"\nTesting {name}: {url}")
                    result = fetcher.fetch(url)
                    
                    if result["success"]:
                        print(f"  ✅ Success! Status: {result['status']}")
                    else:
                        print(f"  ❌ Failed: {result['error']}")
            
            else:
                print(f"❌ Unknown command: {action}")
                print("Available: fetch, json, download, test, quit")
        
        except KeyboardInterrupt:
            print("\n\nExiting...")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    main()
