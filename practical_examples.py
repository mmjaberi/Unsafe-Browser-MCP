#!/usr/bin/env python3
"""
Practical Examples for Unsafe HTTPS Browsing
Ready-to-use scripts for common scenarios
"""

import ssl
import urllib.request
import json
from datetime import datetime

class UnsafeHTTPSFetcher:
    """Simple fetcher with SSL bypass"""
    
    def __init__(self):
        self.ssl_context = ssl.create_default_context()
        self.ssl_context.check_hostname = False
        self.ssl_context.verify_mode = ssl.CERT_NONE
    
    def fetch(self, url, headers=None):
        """Fetch URL with SSL bypass"""
        req = urllib.request.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)')
        
        if headers:
            for key, value in headers.items():
                req.add_header(key, value)
        
        try:
            with urllib.request.urlopen(req, context=self.ssl_context, timeout=30) as response:
                content = response.read().decode('utf-8')
                return {
                    "success": True,
                    "status": response.status,
                    "content": content,
                    "headers": dict(response.headers)
                }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def fetch_json(self, url, headers=None):
        """Fetch and parse JSON"""
        result = self.fetch(url, headers)
        if result["success"]:
            try:
                result["json"] = json.loads(result["content"])
            except:
                pass
        return result


# ============================================================================
# EXAMPLE 1: Check Internal API Status
# ============================================================================

def check_api_health():
    """Check if internal API is healthy"""
    print("\n" + "="*70)
    print("EXAMPLE 1: API Health Check")
    print("="*70)
    
    fetcher = UnsafeHTTPSFetcher()
    
    # Your internal API endpoint
    api_url = "https://your-internal-api.local/health"
    
    print(f"\nChecking: {api_url}")
    result = fetcher.fetch_json(api_url)
    
    if result["success"]:
        print(f"✅ API is UP")
        print(f"   Status: {result['status']}")
        if "json" in result:
            print(f"   Response: {json.dumps(result['json'], indent=2)}")
    else:
        print(f"❌ API is DOWN")
        print(f"   Error: {result['error']}")


# ============================================================================
# EXAMPLE 2: Fetch Data from Multiple Services
# ============================================================================

def fetch_from_multiple_services():
    """Fetch data from multiple internal services"""
    print("\n" + "="*70)
    print("EXAMPLE 2: Multi-Service Data Collection")
    print("="*70)
    
    fetcher = UnsafeHTTPSFetcher()
    
    services = {
        "Users API": "https://users-api.internal/v1/count",
        "Orders API": "https://orders-api.internal/v1/stats",
        "Inventory": "https://inventory.internal/current"
    }
    
    results = {}
    
    for name, url in services.items():
        print(f"\nFetching from {name}...")
        result = fetcher.fetch_json(url)
        
        if result["success"]:
            print(f"  ✅ Success")
            results[name] = result.get("json", result["content"][:100])
        else:
            print(f"  ❌ Failed: {result['error']}")
            results[name] = None
    
    print("\n" + "-"*70)
    print("SUMMARY:")
    print("-"*70)
    for name, data in results.items():
        print(f"{name}: {data}")


# ============================================================================
# EXAMPLE 3: Monitor Service with Alerts
# ============================================================================

def monitor_service_with_alerts(url, check_interval=60, max_checks=10):
    """Monitor a service and alert on failures"""
    print("\n" + "="*70)
    print("EXAMPLE 3: Service Monitoring")
    print("="*70)
    
    fetcher = UnsafeHTTPSFetcher()
    
    print(f"\nMonitoring: {url}")
    print(f"Check interval: {check_interval} seconds")
    print(f"Total checks: {max_checks}")
    print("\nStarting monitoring...\n")
    
    failures = 0
    
    for i in range(max_checks):
        timestamp = datetime.now().strftime("%H:%M:%S")
        result = fetcher.fetch(url)
        
        if result["success"]:
            print(f"[{timestamp}] ✅ Check {i+1}/{max_checks} - Service UP (Status: {result['status']})")
            failures = 0  # Reset failure counter
        else:
            failures += 1
            print(f"[{timestamp}] ❌ Check {i+1}/{max_checks} - Service DOWN ({result['error']})")
            
            # Alert after 3 consecutive failures
            if failures >= 3:
                print(f"\n{'!'*70}")
                print(f"⚠️  ALERT: Service has been down for {failures} consecutive checks!")
                print(f"{'!'*70}\n")
        
        # Don't sleep on last iteration
        if i < max_checks - 1:
            import time
            time.sleep(check_interval)
    
    print("\nMonitoring complete.")


# ============================================================================
# EXAMPLE 4: Test API Authentication
# ============================================================================

def test_api_authentication():
    """Test API with different authentication methods"""
    print("\n" + "="*70)
    print("EXAMPLE 4: API Authentication Testing")
    print("="*70)
    
    fetcher = UnsafeHTTPSFetcher()
    
    api_url = "https://api.internal/protected"
    
    # Test 1: No authentication
    print("\n1. Testing without authentication...")
    result = fetcher.fetch(api_url)
    print(f"   Status: {result.get('status', 'Failed')}")
    
    # Test 2: Bearer token
    print("\n2. Testing with Bearer token...")
    headers = {"Authorization": "Bearer your-token-here"}
    result = fetcher.fetch(api_url, headers=headers)
    print(f"   Status: {result.get('status', 'Failed')}")
    
    # Test 3: API Key
    print("\n3. Testing with API key...")
    headers = {"X-API-Key": "your-api-key-here"}
    result = fetcher.fetch(api_url, headers=headers)
    print(f"   Status: {result.get('status', 'Failed')}")
    
    # Test 4: Basic Auth (in header)
    print("\n4. Testing with custom auth header...")
    import base64
    credentials = base64.b64encode(b"username:password").decode()
    headers = {"Authorization": f"Basic {credentials}"}
    result = fetcher.fetch(api_url, headers=headers)
    print(f"   Status: {result.get('status', 'Failed')}")


# ============================================================================
# EXAMPLE 5: Scrape Internal Dashboard
# ============================================================================

def scrape_internal_dashboard():
    """Scrape data from internal HTML dashboard"""
    print("\n" + "="*70)
    print("EXAMPLE 5: Dashboard Scraping")
    print("="*70)
    
    fetcher = UnsafeHTTPSFetcher()
    
    dashboard_url = "https://dashboard.internal"
    
    print(f"\nScraping: {dashboard_url}")
    result = fetcher.fetch(dashboard_url)
    
    if result["success"]:
        html = result["content"]
        
        # Simple text extraction (for demo - use BeautifulSoup for real scraping)
        print("\n📊 Dashboard Content:")
        
        # Extract title
        if "<title>" in html:
            start = html.find("<title>") + 7
            end = html.find("</title>")
            title = html[start:end]
            print(f"   Title: {title}")
        
        # Count certain elements (example)
        print(f"   Links found: {html.count('<a ')}")
        print(f"   Forms found: {html.count('<form')}")
        print(f"   Content size: {len(html)} bytes")
        
        # You can use BeautifulSoup for more advanced parsing:
        # from bs4 import BeautifulSoup
        # soup = BeautifulSoup(html, 'html.parser')
        # data = soup.find_all('div', class_='metric')
    else:
        print(f"❌ Failed to scrape: {result['error']}")


# ============================================================================
# EXAMPLE 6: Batch Download Files
# ============================================================================

def batch_download_reports():
    """Download multiple reports from internal server"""
    print("\n" + "="*70)
    print("EXAMPLE 6: Batch File Download")
    print("="*70)
    
    fetcher = UnsafeHTTPSFetcher()
    
    files = {
        "daily_report.pdf": "https://reports.internal/daily/2024-01-01.pdf",
        "weekly_summary.xlsx": "https://reports.internal/weekly/summary.xlsx",
        "monthly_stats.csv": "https://reports.internal/monthly/stats.csv"
    }
    
    for filename, url in files.items():
        print(f"\nDownloading: {filename}")
        print(f"  From: {url}")
        
        # Create request
        req = urllib.request.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0')
        
        try:
            # Create SSL context
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            with urllib.request.urlopen(req, context=ssl_context, timeout=30) as response:
                data = response.read()
                
                with open(filename, 'wb') as f:
                    f.write(data)
                
                print(f"  ✅ Downloaded {len(data)} bytes")
        except Exception as e:
            print(f"  ❌ Failed: {e}")


# ============================================================================
# EXAMPLE 7: Compare API Responses
# ============================================================================

def compare_api_environments():
    """Compare API responses across different environments"""
    print("\n" + "="*70)
    print("EXAMPLE 7: Environment Comparison")
    print("="*70)
    
    fetcher = UnsafeHTTPSFetcher()
    
    environments = {
        "Dev": "https://api-dev.internal/config",
        "Staging": "https://api-staging.internal/config",
        "Production": "https://api-prod.internal/config"
    }
    
    responses = {}
    
    for env, url in environments.items():
        print(f"\nFetching {env} config...")
        result = fetcher.fetch_json(url)
        
        if result["success"] and "json" in result:
            responses[env] = result["json"]
            print(f"  ✅ Success")
        else:
            responses[env] = None
            print(f"  ❌ Failed")
    
    # Compare
    print("\n" + "="*70)
    print("COMPARISON:")
    print("="*70)
    
    if all(responses.values()):
        # Check for differences
        dev_keys = set(responses["Dev"].keys()) if responses["Dev"] else set()
        staging_keys = set(responses["Staging"].keys()) if responses["Staging"] else set()
        prod_keys = set(responses["Production"].keys()) if responses["Production"] else set()
        
        print(f"\nConfig keys in Dev: {len(dev_keys)}")
        print(f"Config keys in Staging: {len(staging_keys)}")
        print(f"Config keys in Production: {len(prod_keys)}")
        
        # Find differences
        only_in_dev = dev_keys - staging_keys - prod_keys
        only_in_staging = staging_keys - dev_keys - prod_keys
        only_in_prod = prod_keys - dev_keys - staging_keys
        
        if only_in_dev:
            print(f"\n⚠️  Keys only in Dev: {only_in_dev}")
        if only_in_staging:
            print(f"\n⚠️  Keys only in Staging: {only_in_staging}")
        if only_in_prod:
            print(f"\n⚠️  Keys only in Production: {only_in_prod}")
    else:
        print("\n❌ Cannot compare - some environments failed")


# ============================================================================
# MAIN MENU
# ============================================================================

def main():
    """Interactive menu to run examples"""
    print("\n" + "="*70)
    print("🔓 UNSAFE HTTPS EXAMPLES")
    print("⚠️  WARNING: SSL Certificate Verification DISABLED")
    print("="*70)
    
    examples = {
        "1": ("API Health Check", check_api_health),
        "2": ("Multi-Service Data Collection", fetch_from_multiple_services),
        "3": ("Service Monitoring", lambda: monitor_service_with_alerts(
            "https://your-service.local", check_interval=5, max_checks=5
        )),
        "4": ("API Authentication Testing", test_api_authentication),
        "5": ("Dashboard Scraping", scrape_internal_dashboard),
        "6": ("Batch File Download", batch_download_reports),
        "7": ("Environment Comparison", compare_api_environments),
    }
    
    while True:
        print("\nAvailable Examples:")
        for key, (name, _) in examples.items():
            print(f"  {key}. {name}")
        print("  q. Quit")
        
        choice = input("\nSelect example (1-7 or q): ").strip().lower()
        
        if choice == 'q':
            print("\nExiting...")
            break
        
        if choice in examples:
            _, func = examples[choice]
            try:
                func()
            except KeyboardInterrupt:
                print("\n\nExample interrupted.")
            except Exception as e:
                print(f"\n❌ Error running example: {e}")
        else:
            print("❌ Invalid choice")
    
    print("\n⚠️  Remember: Only use for testing/development!")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
