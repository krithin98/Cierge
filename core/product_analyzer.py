#!/usr/bin/env python3
"""
Product Analyzer - Extracts real product information from any URL
"""

import re
from urllib.parse import urlparse
from typing import Dict, List, Optional
import requests
from bs4 import BeautifulSoup


class ProductAnalyzer:
    """
    Analyzes product URLs to extract meaningful product information
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
    
    def analyze_product_url(self, url: str) -> Optional[Dict[str, any]]:
        """
        Extract product information from any product URL
        """
        print(f"🔍 Analyzing product URL: {url}")
        
        try:
            domain = urlparse(url).netloc.lower()
            
            product_info = {
                'original_url': url,
                'domain': domain,
                'title': None,
                'brand': None,
                'category': None,
                'price': None,
                'search_terms': []
            }
            
            # Method 1: Try to extract from URL structure (works even when blocked)
            url_title = self._extract_from_url_structure(url, domain)
            if url_title:
                product_info['title'] = url_title
            
            # Method 2: Try to scrape the actual page (if not blocked)
            if not product_info['title']:
                scraped_info = self._scrape_product_page(url)
                if scraped_info:
                    product_info.update(scraped_info)
            
            # Method 3: Enhanced analysis if we have a title
            if product_info['title']:
                enhanced_info = self._enhance_product_info(product_info['title'])
                product_info.update(enhanced_info)
                
                print(f"✅ Analyzed product: {product_info['title']}")
                print(f"📂 Category: {product_info['category']}")
                print(f"🏷️ Brand: {product_info['brand']}")
                
                return product_info
            
            print("❌ Could not extract product information")
            return None
            
        except Exception as e:
            print(f"❌ Error analyzing product: {e}")
            return None
    
    def _extract_from_url_structure(self, url: str, domain: str) -> Optional[str]:
        """
        Extract product name from URL structure
        """
        try:
            # Amazon URL patterns
            if 'amazon.com' in domain:
                # Pattern: /Product-Name-With-Dashes/dp/B123456789/
                url_parts = url.split('/')
                for part in url_parts:
                    if '-' in part and len(part) > 10:
                        if 'dp' not in part and not part.startswith('B0') and not part.startswith('ref='):
                            title = part.replace('-', ' ').title()
                            if len(title.split()) >= 3:  # At least 3 words
                                return title
            
            # Walmart URL patterns
            elif 'walmart.com' in domain:
                # Pattern: /Product-Name-With-Dashes/12345678
                url_parts = url.split('/')
                for part in url_parts:
                    if '-' in part and len(part) > 15:
                        if not part.isdigit():
                            title = part.replace('-', ' ').title()
                            if len(title.split()) >= 3:
                                return title
            
            # Target URL patterns
            elif 'target.com' in domain:
                # Pattern: /p/product-name/-/A-12345678
                url_parts = url.split('/')
                for i, part in enumerate(url_parts):
                    if part == 'p' and i + 1 < len(url_parts):
                        next_part = url_parts[i + 1]
                        if '-' in next_part:
                            title = next_part.replace('-', ' ').title()
                            if len(title.split()) >= 2:
                                return title
            
            # Best Buy URL patterns
            elif 'bestbuy.com' in domain:
                # Pattern: /site/product-name/12345678.p
                url_parts = url.split('/')
                for part in url_parts:
                    if '-' in part and not part.endswith('.p') and not part.isdigit():
                        title = part.replace('-', ' ').title()
                        if len(title.split()) >= 2:
                            return title
            
            # Generic pattern matching
            else:
                url_parts = url.split('/')
                for part in url_parts:
                    if '-' in part and len(part) > 8:
                        # Skip common URL parts
                        if part.lower() not in ['product', 'item', 'buy', 'shop', 'store']:
                            potential_title = part.replace('-', ' ').replace('_', ' ').title()
                            if len(potential_title.split()) >= 2:
                                return potential_title
            
            return None
            
        except Exception as e:
            print(f"❌ URL structure extraction failed: {e}")
            return None
    
    def _scrape_product_page(self, url: str) -> Optional[Dict[str, str]]:
        """
        Try to scrape product information directly from the page
        """
        try:
            response = self.session.get(url, timeout=10)
            
            if response.status_code != 200:
                return None
            
            # Check if we're blocked (small page size usually indicates blocking)
            if len(response.content) < 5000:
                return None
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            scraped_info = {}
            
            # Try to extract title from various selectors
            title_selectors = [
                '#productTitle',  # Amazon
                'h1[data-testid="product-title"]',  # Walmart
                'h1[data-test="product-title"]',  # Target
                '.sku-title',  # Best Buy
                'h1.product-title',  # Generic
                'h1'  # Fallback
            ]
            
            for selector in title_selectors:
                element = soup.select_one(selector)
                if element:
                    title = element.get_text().strip()
                    if len(title) > 5:  # Reasonable title length
                        scraped_info['title'] = title
                        break
            
            # Try to extract price
            price_selectors = [
                '.a-price-whole',  # Amazon
                '[data-testid="price-current"]',  # Walmart
                '[data-test="product-price"]',  # Target
                '.sr-only:contains("current price")',  # Best Buy
                '.price'  # Generic
            ]
            
            for selector in price_selectors:
                element = soup.select_one(selector)
                if element:
                    price_text = element.get_text().strip()
                    price = self._extract_price_from_text(price_text)
                    if price:
                        scraped_info['price'] = price
                        break
            
            return scraped_info if scraped_info else None
            
        except Exception as e:
            print(f"❌ Page scraping failed: {e}")
            return None
    
    def _enhance_product_info(self, title: str) -> Dict[str, any]:
        """
        Enhance product information by analyzing the title
        """
        enhanced_info = {
            'brand': None,
            'category': None,
            'search_terms': []
        }
        
        if not title:
            return enhanced_info
        
        title_lower = title.lower()
        words = title.split()
        
        # Extract brand (usually first word)
        if words:
            potential_brand = words[0]
            # Check if it looks like a brand name
            if len(potential_brand) > 2 and not potential_brand.lower() in ['the', 'a', 'an']:
                enhanced_info['brand'] = potential_brand
        
        # Categorize product
        enhanced_info['category'] = self._categorize_product(title_lower)
        
        # Generate search terms
        enhanced_info['search_terms'] = self._generate_search_terms(title)
        
        return enhanced_info
    
    def _categorize_product(self, title_lower: str) -> str:
        """
        Categorize product based on title keywords
        """
        categories = {
            'lighting': ['lamp', 'light', 'led', 'bulb', 'fixture', 'chandelier', 'sconce', 'nightstand'],
            'electronics': ['iphone', 'phone', 'smartphone', 'tablet', 'ipad', 'laptop', 'computer', 'tv', 'monitor'],
            'furniture': ['chair', 'table', 'desk', 'sofa', 'bed', 'dresser', 'cabinet', 'shelf'],
            'kitchen': ['pot', 'pan', 'knife', 'blender', 'mixer', 'toaster', 'microwave', 'refrigerator'],
            'clothing': ['shirt', 'pants', 'dress', 'shoes', 'jacket', 'sweater', 'jeans', 'sneakers'],
            'home_decor': ['pillow', 'curtain', 'rug', 'mirror', 'frame', 'vase', 'candle'],
            'beauty': ['makeup', 'skincare', 'perfume', 'shampoo', 'lotion', 'cream'],
            'sports': ['bike', 'treadmill', 'weights', 'yoga', 'fitness', 'exercise'],
            'automotive': ['car', 'tire', 'battery', 'oil', 'brake', 'filter'],
            'books': ['book', 'novel', 'textbook', 'guide', 'manual'],
            'toys': ['toy', 'game', 'puzzle', 'doll', 'action figure', 'lego']
        }
        
        for category, keywords in categories.items():
            if any(keyword in title_lower for keyword in keywords):
                return category
        
        return 'general'
    
    def _generate_search_terms(self, title: str) -> List[str]:
        """
        Generate effective search terms from product title
        """
        if not title:
            return []
        
        # Clean and split title
        words = re.findall(r'\b\w+\b', title.lower())
        
        # Remove common stop words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'with', 'for', 'of', 'in', 'on', 'at', 'by', 'from',
            'up', 'about', 'into', 'through', 'during', 'before', 'after', 'above', 'below',
            'to', 'from', 'up', 'down', 'in', 'out', 'off', 'over', 'under', 'again', 'further',
            'then', 'once'
        }
        
        # Filter words
        meaningful_words = [
            word for word in words 
            if word not in stop_words and len(word) > 2
        ]
        
        # Return top 6 most meaningful terms
        return meaningful_words[:6]
    
    def _extract_price_from_text(self, text: str) -> Optional[float]:
        """
        Extract numeric price from text
        """
        if not text:
            return None
        
        # Look for price patterns
        price_patterns = [
            r'\$(\d{1,4}(?:,\d{3})*(?:\.\d{2})?)',  # $1,234.56
            r'(\d{1,4}(?:,\d{3})*(?:\.\d{2})?)\s*dollars?',  # 1234 dollars
            r'Price:?\s*\$?(\d{1,4}(?:,\d{3})*(?:\.\d{2})?)',  # Price: $123
        ]
        
        for pattern in price_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                try:
                    return float(matches[0].replace(',', ''))
                except ValueError:
                    continue
        
        return None


def test_product_analyzer():
    """Test the product analyzer"""
    
    analyzer = ProductAnalyzer()
    
    test_urls = [
        "https://www.amazon.com/Dawnwake-Mushroom-Nightstand-Dimmable-Aesthetic/dp/B0D1FRDFFX/",
        "https://www.walmart.com/ip/Apple-iPhone-15-Pro-256GB-Blue-Titanium-Unlocked/5090318395",
        "https://www.target.com/p/mushroom-table-lamp-brass-project-62/-/A-53324557"
    ]
    
    print("🧪 TESTING PRODUCT ANALYZER")
    print("="*50)
    
    for url in test_urls:
        print(f"\n📍 Testing: {url}")
        print("-" * 40)
        
        result = analyzer.analyze_product_url(url)
        
        if result:
            print(f"✅ Success!")
            print(f"   Title: {result['title']}")
            print(f"   Brand: {result['brand']}")
            print(f"   Category: {result['category']}")
            print(f"   Search Terms: {result['search_terms']}")
            if result['price']:
                print(f"   Price: ${result['price']}")
        else:
            print("❌ Failed to analyze")


if __name__ == "__main__":
    test_product_analyzer()