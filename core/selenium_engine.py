#!/usr/bin/env python3
"""
Selenium Engine with Proxy Rotation
Real browser automation that bypasses anti-bot detection
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from fake_useragent import UserAgent
import time
import random
from typing import List, Optional, Dict
import requests


class ProxyRotator:
    """Manages proxy rotation for Selenium"""
    
    def __init__(self):
        # Free proxy sources (in production, use paid proxy service)
        self.proxy_sources = [
            "https://www.proxy-list.download/api/v1/get?type=http",
            "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
        ]
        self.working_proxies = []
        self.current_proxy_index = 0
        self.refresh_proxies()
    
    def refresh_proxies(self):
        """Fetch fresh proxy list"""
        print("🔄 Refreshing proxy list...")
        
        for source in self.proxy_sources:
            try:
                response = requests.get(source, timeout=10)
                if response.status_code == 200:
                    proxies = response.text.strip().split('\n')
                    # Test a few proxies to make sure they work
                    for proxy in proxies[:10]:  # Test first 10
                        if self.test_proxy(proxy.strip()):
                            self.working_proxies.append(proxy.strip())
                            if len(self.working_proxies) >= 5:  # Get at least 5 working proxies
                                break
                    
                    if self.working_proxies:
                        break
                        
            except Exception as e:
                print(f"❌ Failed to fetch proxies from {source}: {e}")
        
        print(f"✅ Found {len(self.working_proxies)} working proxies")
    
    def test_proxy(self, proxy: str) -> bool:
        """Test if a proxy works"""
        try:
            proxies = {
                'http': f'http://{proxy}',
                'https': f'http://{proxy}'
            }
            response = requests.get('http://httpbin.org/ip', proxies=proxies, timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def get_next_proxy(self) -> Optional[str]:
        """Get next working proxy"""
        if not self.working_proxies:
            return None
        
        proxy = self.working_proxies[self.current_proxy_index]
        self.current_proxy_index = (self.current_proxy_index + 1) % len(self.working_proxies)
        return proxy


class SeleniumEngine:
    """
    Real Selenium engine with anti-detection measures
    """
    
    def __init__(self, use_proxy: bool = True):
        self.use_proxy = use_proxy
        self.proxy_rotator = ProxyRotator() if use_proxy else None
        self.user_agent = UserAgent()
        self.driver = None
    
    def create_driver(self, proxy: Optional[str] = None) -> webdriver.Chrome:
        """Create Chrome driver with anti-detection settings"""
        
        options = Options()
        
        # Anti-detection settings
        # options.add_argument('--headless')  # Disable headless for testing
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-plugins-discovery')
        options.add_argument('--disable-web-security')
        options.add_argument('--allow-running-insecure-content')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Additional stealth settings
        options.add_argument('--disable-features=VizDisplayCompositor')
        options.add_argument('--window-size=1920,1080')
        
        # Random user agent
        user_agent = self.user_agent.random
        options.add_argument(f'--user-agent={user_agent}')
        
        # Proxy settings
        if proxy and self.use_proxy:
            options.add_argument(f'--proxy-server=http://{proxy}')
            print(f"🌐 Using proxy: {proxy}")
        
        # Create driver
        try:
            import os
            
            # Get Chrome driver path and fix it immediately
            raw_driver_path = ChromeDriverManager().install()
            print(f"📍 WebDriver Manager returned: {raw_driver_path}")
            
            # Always fix the path - WebDriverManager has a bug
            driver_dir = os.path.dirname(raw_driver_path)
            driver_path = os.path.join(driver_dir, 'chromedriver')
            
            if os.path.exists(driver_path):
                print(f"📍 Using correct chromedriver: {driver_path}")
            else:
                print(f"❌ Could not find chromedriver in {driver_dir}")
                print(f"📁 Directory contents: {os.listdir(driver_dir)}")
                return None
            
            # Make sure the driver is executable
            os.chmod(driver_path, 0o755)
            print(f"📍 Made executable: {driver_path}")
            
            # Test if the driver is actually executable
            if not os.access(driver_path, os.X_OK):
                print(f"❌ Driver is not executable: {driver_path}")
                return None
            
            driver = webdriver.Chrome(
                service=webdriver.chrome.service.Service(driver_path),
                options=options
            )
            
            # Execute script to hide automation
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            return driver
            
        except Exception as e:
            print(f"❌ Failed to create driver: {e}")
            return None
    
    def start_session(self) -> bool:
        """Start a new Selenium session"""
        
        # Try with proxy first, then without
        if self.use_proxy and self.proxy_rotator:
            proxy = self.proxy_rotator.get_next_proxy()
            self.driver = self.create_driver(proxy)
        
        # Fallback to no proxy
        if not self.driver:
            print("🔄 Proxy failed, trying without proxy...")
            self.driver = self.create_driver(None)
        
        if self.driver:
            print("✅ Selenium session started")
            return True
        else:
            print("❌ Failed to start Selenium session")
            return False
    
    def google_search(self, query: str) -> List[Dict[str, str]]:
        """
        Perform real Google search and extract results
        """
        if not self.driver:
            if not self.start_session():
                return []
        
        try:
            print(f"🔍 Searching Google for: '{query}'")
            
            # Navigate to Google
            self.driver.get("https://www.google.com")
            
            # Add random delay to seem human
            time.sleep(random.uniform(2, 4))
            
            # Find search box and enter query
            search_box = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "q"))
            )
            
            # Type query with human-like delays
            for char in query:
                search_box.send_keys(char)
                time.sleep(random.uniform(0.05, 0.15))
            
            # Submit search
            search_box.submit()
            
            # Wait for results to load with longer timeout
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.g, .g"))
            )
            
            # Add delay before scraping
            time.sleep(random.uniform(2, 4))
            
            # Extract search results
            results = []
            result_elements = self.driver.find_elements(By.CSS_SELECTOR, "div.g")
            
            for element in result_elements[:15]:  # Get first 15 results
                try:
                    # Extract title and URL
                    title_element = element.find_element(By.CSS_SELECTOR, "h3")
                    link_element = element.find_element(By.CSS_SELECTOR, "a")
                    
                    title = title_element.text.strip()
                    url = link_element.get_attribute("href")
                    
                    # Extract snippet if available
                    snippet = ""
                    try:
                        snippet_element = element.find_element(By.CSS_SELECTOR, ".VwiC3b, .s3v9rd")
                        snippet = snippet_element.text.strip()
                    except:
                        pass
                    
                    if title and url and url.startswith("http"):
                        results.append({
                            'title': title,
                            'url': url,
                            'snippet': snippet
                        })
                
                except Exception as e:
                    continue  # Skip this result if extraction fails
            
            print(f"✅ Found {len(results)} search results")
            return results
            
        except TimeoutException:
            print("❌ Google search timed out")
            return []
        except Exception as e:
            print(f"❌ Google search failed: {e}")
            return []
    
    def close_session(self):
        """Close Selenium session"""
        if self.driver:
            try:
                self.driver.quit()
                print("✅ Selenium session closed")
            except:
                pass
            finally:
                self.driver = None
    
    def __del__(self):
        """Cleanup on deletion"""
        self.close_session()


def test_selenium_engine():
    """Test the Selenium engine"""
    
    print("🧪 TESTING SELENIUM ENGINE")
    print("="*50)
    
    # Create engine (start without proxy for testing)
    engine = SeleniumEngine(use_proxy=False)
    
    try:
        # Test Google search
        results = engine.google_search("mushroom table lamp buy online")
        
        if results:
            print(f"\n🎯 FOUND {len(results)} REAL SEARCH RESULTS:")
            
            for i, result in enumerate(results[:5], 1):
                print(f"\n#{i}")
                print(f"   Title: {result['title']}")
                print(f"   URL: {result['url']}")
                if result['snippet']:
                    print(f"   Snippet: {result['snippet'][:100]}...")
        else:
            print("❌ No search results found")
    
    finally:
        engine.close_session()


if __name__ == "__main__":
    test_selenium_engine()