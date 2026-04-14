#!/usr/bin/env python3
"""
URL Verifier - Checks that product URLs actually work
"""

import requests
from typing import List, Dict, Optional
from dataclasses import dataclass
import time
import random


@dataclass
class VerifiedProduct:
    title: str
    url: str
    retailer: str
    price: Optional[str] = None
    snippet: str = ""
    verified: bool = False
    response_time: float = 0.0


class URLVerifier:
    """
    Verifies that product URLs actually work and are accessible
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
    
    def verify_products(self, products: List[Dict[str, str]]) -> List[VerifiedProduct]:
        """
        Verify that product URLs actually work
        """
        print(f"🔍 Verifying {len(products)} product URLs...")
        
        verified_products = []
        
        for product in products:
            verified = self._verify_single_url(product)
            if verified:
                verified_products.append(verified)
            
            # Be respectful - add delay between requests
            time.sleep(random.uniform(0.5, 1.5))
        
        print(f"✅ Verified {len(verified_products)} working URLs")
        return verified_products
    
    def _verify_single_url(self, product: Dict[str, str]) -> Optional[VerifiedProduct]:
        """
        Verify a single product URL
        """
        url = product.get('url', '')
        title = product.get('title', '')
        retailer = product.get('retailer', 'Unknown')
        
        if not url or not title:
            return None
        
        try:
            start_time = time.time()
            
            # Make HEAD request first (faster)
            response = self.session.head(url, timeout=10, allow_redirects=True)
            
            response_time = time.time() - start_time
            
            # Check if URL is accessible
            if response.status_code in [200, 301, 302]:
                print(f"✅ {retailer}: {url[:60]}... (HTTP {response.status_code})")
                
                return VerifiedProduct(
                    title=title,
                    url=url,
                    retailer=retailer,
                    price=product.get('price'),
                    snippet=product.get('snippet', ''),
                    verified=True,
                    response_time=response_time
                )
            
            # If HEAD fails, try GET request
            elif response.status_code >= 400:
                response = self.session.get(url, timeout=10, allow_redirects=True)
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    print(f"✅ {retailer}: {url[:60]}... (HTTP {response.status_code} via GET)")
                    
                    return VerifiedProduct(
                        title=title,
                        url=url,
                        retailer=retailer,
                        price=product.get('price'),
                        snippet=product.get('snippet', ''),
                        verified=True,
                        response_time=response_time
                    )
                else:
                    print(f"❌ {retailer}: {url[:60]}... (HTTP {response.status_code})")
                    return None
            
            else:
                print(f"❌ {retailer}: {url[:60]}... (HTTP {response.status_code})")
                return None
        
        except requests.exceptions.Timeout:
            print(f"⏰ {retailer}: {url[:60]}... (Timeout)")
            return None
        except requests.exceptions.ConnectionError:
            print(f"🔌 {retailer}: {url[:60]}... (Connection Error)")
            return None
        except Exception as e:
            print(f"❌ {retailer}: {url[:60]}... (Error: {e})")
            return None


def test_url_verifier():
    """Test the URL verifier"""
    
    # Test with some real product URLs
    test_products = [
        {
            'title': 'DEWENWILS Mushroom Table Lamp',
            'url': 'https://www.amazon.com/DEWENWILS-Mushroom-Dimmable-Bedside-Nightstand/dp/B08T1YXQPX/',
            'retailer': 'Amazon',
            'price': '$29.99'
        },
        {
            'title': 'Mainstays Mushroom Table Lamp',
            'url': 'https://www.walmart.com/ip/Mainstays-13-Mushroom-Table-Lamp-with-Fabric-Shade-White/55126267',
            'retailer': 'Walmart',
            'price': '$19.97'
        },
        {
            'title': 'Fake Product (Should Fail)',
            'url': 'https://www.example.com/fake-product-12345',
            'retailer': 'Fake Store',
            'price': '$99.99'
        }
    ]
    
    print("🧪 TESTING URL VERIFIER")
    print("="*50)
    
    verifier = URLVerifier()
    verified_products = verifier.verify_products(test_products)
    
    if verified_products:
        print(f"\n🎯 VERIFIED {len(verified_products)} WORKING PRODUCTS:")
        
        for i, product in enumerate(verified_products, 1):
            print(f"\n#{i} - {product.retailer}")
            print(f"   Title: {product.title}")
            print(f"   Price: {product.price or 'Not listed'}")
            print(f"   Response Time: {product.response_time:.2f}s")
            print(f"   🔗 WORKING URL: {product.url}")
    else:
        print("❌ No working URLs found")


if __name__ == "__main__":
    test_url_verifier()