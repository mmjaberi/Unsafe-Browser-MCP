#!/usr/bin/env python3
"""
Enhanced Async Simple HTTPS Fetcher
Features: Retry logic, better logging, async operations, progress bars
"""

import asyncio
import aiohttp
import ssl
import json
import os
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum
import time

# ============================================================================
# CUSTOM ERROR TYPES
# ============================================================================

class FetchError(Exception):
    """Base exception for fetch errors"""
    pass

class SSLError(FetchError):
    """SSL certificate related errors"""
    pass

class TimeoutError(FetchError):
    """Request timeout errors"""
    pass

class NetworkError(FetchError):
    """Network connectivity errors"""
    pass

class HTTPError(FetchError):
    """HTTP status code errors"""
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        super().__init__(f"HTTP {status_code}: {message}")

class ParseError(FetchError):
    """Content parsing errors"""
    pass


# ============================================================================
# LOGGING SETUP
# ============================================================================

class ColoredFormatter(logging.Formatter):
    """Colored log formatter"""
    
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
    }
    RESET = '\033[0m'
    
    def format(self, record):
        log_color = self.COLORS.get(record.levelname, self.RESET)
        record.levelname = f"{log_color}{record.levelname}{self.RESET}"
        return super().format(record)

def setup_logging(log_file: str = "/app/logs/fetcher.log", level=logging.INFO):
    """Setup structured logging with file and console outputs"""
    
    # Create logs directory
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    # Root logger
    logger = logging.getLogger()
    logger.setLevel(level)
    
    # File handler - JSON structured logs
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "module": "%(name)s", "message": "%(message)s"}'
    )
    file_handler.setFormatter(file_formatter)
    
    # Console handler - colored output
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_formatter = ColoredFormatter(
        '%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

logger = setup_logging()


# ============================================================================
# PROGRESS BAR
# ============================================================================

class ProgressBar:
    """Simple progress bar for downloads"""
    
    def __init__(self, total: int, prefix: str = "Downloading"):
        self.total = total
        self.current = 0
        self.prefix = prefix
        self.start_time = time.time()
    
    def update(self, chunk_size: int):
        """Update progress"""
        self.current += chunk_size
        percent = (self.current / self.total) * 100 if self.total > 0 else 0
        
        # Calculate speed
        elapsed = time.time() - self.start_time
        speed = self.current / elapsed if elapsed > 0 else 0
        
        # Format sizes
        current_mb = self.current / (1024 * 1024)
        total_mb = self.total / (1024 * 1024)
        speed_mb = speed / (1024 * 1024)
        
        # Progress bar
        bar_length = 40
        filled = int(bar_length * percent / 100)
        bar = '█' * filled + '░' * (bar_length - filled)
        
        print(f"\r{self.prefix}: [{bar}] {percent:.1f}% ({current_mb:.2f}/{total_mb:.2f} MB) @ {speed_mb:.2f} MB/s", end='')
        
        if self.current >= self.total:
            print()  # New line when complete


# ============================================================================
# ENHANCED ASYNC FETCHER
# ============================================================================

class EnhancedAsyncFetcher:
    """Async HTTPS fetcher with retry logic, logging, and progress tracking"""
    
    def __init__(self, 
                 max_retries: int = 3,
                 retry_delay: float = 1.0,
                 timeout: int = 30,
                 proxy: Optional[str] = None,
                 verify_ssl: bool = False):
        
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.timeout = timeout
        self.proxy = proxy
        self.verify_ssl = verify_ssl
        self.download_dir = "/app/downloads"
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Create SSL context
        self.ssl_context = ssl.create_default_context()
        if not verify_ssl:
            self.ssl_context.check_hostname = False
            self.ssl_context.verify_mode = ssl.CERT_NONE
        
        logger.info(f"Fetcher initialized (SSL verify: {verify_ssl}, Max retries: {max_retries})")
    
    async def __aenter__(self):
        """Context manager entry"""
        await self.create_session()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        await self.close_session()
    
    async def create_session(self):
        """Create aiohttp session"""
        if self.session is None:
            connector = aiohttp.TCPConnector(ssl=self.ssl_context)
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            
            self.session = aiohttp.ClientSession(
                connector=connector,
                timeout=timeout,
                headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'}
            )
            logger.debug("Session created")
    
    async def close_session(self):
        """Close aiohttp session"""
        if self.session:
            await self.session.close()
            self.session = None
            logger.debug("Session closed")
    
    async def _retry_wrapper(self, func, *args, **kwargs):
        """Wrapper for retry logic with exponential backoff"""
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                logger.debug(f"Attempt {attempt + 1}/{self.max_retries}")
                return await func(*args, **kwargs)
            
            except aiohttp.ClientSSLError as e:
                last_error = SSLError(f"SSL certificate error: {str(e)}")
                logger.warning(f"SSL error on attempt {attempt + 1}: {e}")
            
            except asyncio.TimeoutError as e:
                last_error = TimeoutError(f"Request timeout after {self.timeout}s")
                logger.warning(f"Timeout on attempt {attempt + 1}")
            
            except aiohttp.ClientConnectionError as e:
                last_error = NetworkError(f"Connection error: {str(e)}")
                logger.warning(f"Connection error on attempt {attempt + 1}: {e}")
            
            except aiohttp.ClientError as e:
                last_error = NetworkError(f"Client error: {str(e)}")
                logger.warning(f"Client error on attempt {attempt + 1}: {e}")
            
            # Exponential backoff
            if attempt < self.max_retries - 1:
                delay = self.retry_delay * (2 ** attempt)
                logger.info(f"Retrying in {delay}s...")
                await asyncio.sleep(delay)
        
        # All retries failed
        logger.error(f"All {self.max_retries} attempts failed: {last_error}")
        raise last_error
    
    async def fetch(self, url: str, headers: Dict[str, str] = None) -> Dict[str, Any]:
        """Fetch URL with retry logic and logging"""
        
        logger.info(f"Fetching: {url}")
        start_time = time.time()
        
        if not self.session:
            await self.create_session()
        
        async def _fetch():
            request_headers = headers or {}
            
            async with self.session.get(url, headers=request_headers, proxy=self.proxy) as response:
                
                # Check HTTP status
                if response.status >= 400:
                    error_text = await response.text()
                    raise HTTPError(response.status, error_text[:200])
                
                content = await response.read()
                
                # Try to decode
                try:
                    text_content = content.decode('utf-8')
                except UnicodeDecodeError:
                    text_content = content.decode('latin-1', errors='ignore')
                
                elapsed = time.time() - start_time
                logger.info(f"✅ Success: {url} ({response.status}) - {len(content)} bytes in {elapsed:.2f}s")
                
                return {
                    "success": True,
                    "url": str(response.url),
                    "status": response.status,
                    "headers": dict(response.headers),
                    "content": text_content,
                    "size": len(content),
                    "elapsed": elapsed,
                    "ssl_verified": self.verify_ssl
                }
        
        try:
            return await self._retry_wrapper(_fetch)
        except FetchError as e:
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__,
                "url": url,
                "elapsed": time.time() - start_time
            }
    
    async def fetch_json(self, url: str, headers: Dict[str, str] = None) -> Dict[str, Any]:
        """Fetch and parse JSON response"""
        
        logger.info(f"Fetching JSON: {url}")
        result = await self.fetch(url, headers)
        
        if result["success"]:
            try:
                result["json"] = json.loads(result["content"])
                logger.debug(f"JSON parsed successfully: {len(result['json'])} items")
            except json.JSONDecodeError as e:
                error_msg = f"JSON parse error: {str(e)}"
                logger.error(error_msg)
                result["json_error"] = error_msg
                raise ParseError(error_msg)
        
        return result
    
    async def download_file(self, url: str, filename: str, show_progress: bool = True) -> Dict[str, Any]:
        """Download file with progress bar"""
        
        logger.info(f"Downloading: {url} -> {filename}")
        start_time = time.time()
        
        if not self.session:
            await self.create_session()
        
        # Ensure proper path
        if not filename.startswith('/'):
            filepath = os.path.join(self.download_dir, filename)
        else:
            filepath = filename
        
        async def _download():
            async with self.session.get(url, proxy=self.proxy) as response:
                
                if response.status >= 400:
                    raise HTTPError(response.status, f"Failed to download file")
                
                total_size = int(response.headers.get('content-length', 0))
                
                # Initialize progress bar
                progress = ProgressBar(total_size, f"Downloading {filename}") if show_progress and total_size > 0 else None
                
                # Download in chunks
                downloaded = 0
                with open(filepath, 'wb') as f:
                    async for chunk in response.content.iter_chunked(8192):
                        f.write(chunk)
                        downloaded += len(chunk)
                        if progress:
                            progress.update(len(chunk))
                
                elapsed = time.time() - start_time
                logger.info(f"✅ Downloaded: {filename} ({downloaded} bytes in {elapsed:.2f}s)")
                
                return {
                    "success": True,
                    "url": url,
                    "output_path": filepath,
                    "size": downloaded,
                    "elapsed": elapsed,
                    "message": f"✅ Downloaded {downloaded} bytes! Saved to: downloads/{filename}"
                }
        
        try:
            return await self._retry_wrapper(_download)
        except FetchError as e:
            logger.error(f"Download failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__,
                "url": url
            }
    
    async def batch_fetch(self, urls: List[str]) -> List[Dict[str, Any]]:
        """Fetch multiple URLs concurrently"""
        
        logger.info(f"Batch fetching {len(urls)} URLs")
        start_time = time.time()
        
        tasks = [self.fetch(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Convert exceptions to error dicts
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append({
                    "success": False,
                    "error": str(result),
                    "url": urls[i]
                })
            else:
                processed_results.append(result)
        
        elapsed = time.time() - start_time
        successful = sum(1 for r in processed_results if r.get("success"))
        
        logger.info(f"Batch complete: {successful}/{len(urls)} successful in {elapsed:.2f}s")
        
        return processed_results


# ============================================================================
# CLI INTERFACE
# ============================================================================

async def main():
    """Enhanced CLI interface"""
    
    print("="*70)
    print("🚀 ENHANCED ASYNC HTTPS FETCHER")
    print("⚠️  WARNING: SSL Certificate Verification DISABLED")
    print("="*70)
    print("\n📋 Commands:")
    print("  fetch <url>                - Fetch URL content")
    print("  json <url>                 - Fetch and parse JSON")
    print("  download <url> <filename>  - Download file with progress")
    print("  batch <url1> <url2> ...    - Fetch multiple URLs concurrently")
    print("  test                       - Test with bad SSL sites")
    print("  logs                       - Show recent logs")
    print("  stats                      - Show fetcher statistics")
    print("  quit                       - Exit")
    print("="*70)
    print("\n💡 Features:")
    print("  ✅ Auto-retry with exponential backoff")
    print("  ✅ Structured logging to file & console")
    print("  ✅ Progress bars for downloads")
    print("  ✅ Async concurrent requests")
    print("  ✅ Granular error types")
    print("="*70)
    
    # Create fetcher with context manager
    async with EnhancedAsyncFetcher(max_retries=3, retry_delay=1.0) as fetcher:
        
        while True:
            try:
                command = input("\n> ").strip().split(maxsplit=1)
                
                if not command:
                    continue
                
                action = command[0].lower()
                
                if action in ["quit", "exit"]:
                    logger.info("Exiting...")
                    break
                
                elif action == "fetch":
                    if len(command) < 2:
                        print("❌ Usage: fetch <url>")
                        continue
                    
                    url = command[1]
                    result = await fetcher.fetch(url)
                    
                    if result["success"]:
                        print(f"\n✅ Success!")
                        print(f"📊 Status: {result['status']}")
                        print(f"📄 Size: {result['size']:,} bytes")
                        print(f"⏱️  Time: {result['elapsed']:.2f}s")
                        print(f"🔐 SSL Verified: {result['ssl_verified']}")
                        print(f"\n📝 Content Preview:")
                        print(result['content'][:500])
                    else:
                        print(f"\n❌ Error ({result['error_type']}): {result['error']}")
                
                elif action == "json":
                    if len(command) < 2:
                        print("❌ Usage: json <url>")
                        continue
                    
                    url = command[1]
                    try:
                        result = await fetcher.fetch_json(url)
                        
                        if result["success"] and "json" in result:
                            print(f"\n✅ Success!")
                            print(f"📊 Status: {result['status']}")
                            print(f"⏱️  Time: {result['elapsed']:.2f}s")
                            print(f"\n📋 JSON Data:")
                            print(json.dumps(result['json'], indent=2)[:1000])
                    except ParseError as e:
                        print(f"\n❌ {e}")
                
                elif action == "download":
                    parts = command[1].split() if len(command) > 1 else []
                    if len(parts) < 2:
                        print("❌ Usage: download <url> <filename>")
                        continue
                    
                    url, filename = parts[0], parts[1]
                    result = await fetcher.download_file(url, filename, show_progress=True)
                    
                    if result["success"]:
                        print(f"\n{result['message']}")
                        print(f"⏱️  Time: {result['elapsed']:.2f}s")
                    else:
                        print(f"\n❌ Error ({result['error_type']}): {result['error']}")
                
                elif action == "batch":
                    if len(command) < 2:
                        print("❌ Usage: batch <url1> <url2> <url3> ...")
                        continue
                    
                    urls = command[1].split()
                    print(f"\n🚀 Fetching {len(urls)} URLs concurrently...")
                    
                    results = await fetcher.batch_fetch(urls)
                    
                    print(f"\n📊 Results:")
                    for i, result in enumerate(results, 1):
                        if result.get("success"):
                            print(f"  {i}. ✅ {result['url']} ({result['status']}) - {result['size']} bytes")
                        else:
                            print(f"  {i}. ❌ {result['url']} - {result.get('error', 'Unknown error')}")
                
                elif action == "test":
                    print("\n🧪 Testing with known bad SSL certificates...\n")
                    
                    test_urls = [
                        "https://self-signed.badssl.com/",
                        "https://expired.badssl.com/",
                        "https://wrong.host.badssl.com/",
                    ]
                    
                    results = await fetcher.batch_fetch(test_urls)
                    
                    for result in results:
                        if result.get("success"):
                            print(f"✅ {result['url']} - Status: {result['status']}")
                        else:
                            print(f"❌ {result['url']} - {result.get('error_type', 'Error')}")
                
                elif action == "logs":
                    print("\n📋 Recent logs (last 20 lines):")
                    try:
                        with open("/app/logs/fetcher.log", "r") as f:
                            lines = f.readlines()
                            for line in lines[-20:]:
                                print(line.strip())
                    except FileNotFoundError:
                        print("No logs found yet")
                
                elif action == "stats":
                    print("\n📊 Fetcher Statistics:")
                    print(f"  Max Retries: {fetcher.max_retries}")
                    print(f"  Retry Delay: {fetcher.retry_delay}s")
                    print(f"  Timeout: {fetcher.timeout}s")
                    print(f"  SSL Verify: {fetcher.verify_ssl}")
                    print(f"  Proxy: {fetcher.proxy or 'None'}")
                    print(f"  Session Active: {fetcher.session is not None}")
                
                else:
                    print(f"❌ Unknown command: {action}")
                    print("Type 'help' to see available commands")
            
            except KeyboardInterrupt:
                print("\n\nInterrupted...")
                continue
            except Exception as e:
                logger.exception(f"Unexpected error: {e}")
                print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    print("\n🚀 Starting Enhanced Async Fetcher...\n")
    asyncio.run(main())
