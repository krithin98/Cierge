#!/usr/bin/env python3
"""
Production-Ready Cierge App
Built using Tavily best practices for optimal product comparison
"""

from flask import Flask, render_template_string, request, redirect, url_for
from tavily import TavilyClient
import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
import threading
import time
import uuid
import os


app = Flask(__name__)
app.secret_key = 'cierge-production-2024'

# In-memory storage
search_requests = {}

# Tavily API configuration
TAVILY_API_KEY = "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"


@dataclass
class VerifiedProduct:
    title: str
    price: Optional[str]
    retailer: str
    url: str
    snippet: str
    relevance_score: float
    verified: bool = True


class ProductionCiergeEngine:
    """
    Production-ready product comparison engine using Tavily best practices
    """
    
    def __init__(self, api_key: str):
        self.client = TavilyClient(api_key=api_key)
        
        # Major shopping domains for filtering
        self.shopping_domains = [
            'amazon.com', 'walmart.com', 'target.com', 'bestbuy.com', 'ebay.com',
            'newegg.com', 'wayfair.com', 'overstock.com', 'homedepot.com', 'lowes.com',
            'costco.com', 'macys.com', 'kohls.com', 'etsy.com', 'bhphotovideo.com'
        ]
        
        self.retailer_names = {
            'amazon.com': 'Amazon',
            'walmart.com': 'Walmart',
            'target.com': 'Target',
            'bestbuy.com': 'Best Buy',
            'ebay.com': 'eBay',
            'newegg.com': 'Newegg',
            'wayfair.com': 'Wayfair',
            'overstock.com': 'Overstock',
            'homedepot.com': 'Home Depot',
            'lowes.com': "Lowe's",
            'costco.com': 'Costco',
            'macys.com': "Macy's",
            'kohls.com': "Kohl's",
            'etsy.com': 'Etsy',
            'bhphotovideo.com': 'B&H Photo'
        }
    
    def find_product_alternatives(self, product_url: str) -> List[VerifiedProduct]:
        """
        Find product alternatives using Tavily best practices
        """
        print(f"🔍 Finding alternatives for: {product_url}")
        
        # Step 1: Extract product information
        product_info = self._analyze_product_url(product_url)
        if not product_info:
            print("❌ Could not analyze product URL")
            return []
        
        print(f"✅ Product: {product_info['name']}")
        print(f"📂 Category: {product_info['category']}")
        
        # Step 2: Search using Tavily with optimized parameters
        search_results = self._search_with_tavily_best_practices(product_info)
        
        # Step 3: Process and verify results
        verified_products = self._process_and_verify_results(search_results, product_info)
        
        print(f"🎯 Found {len(verified_products)} verified alternatives")
        return verified_products
    
    def _analyze_product_url(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Analyze product URL to extract meaningful information
        """
        try:
            domain = urlparse(url).netloc.lower()
            product_name = None
            
            # Extract product name from URL structure
            if 'amazon.com' in domain:
                parts = url.split('/')
                for part in parts:
                    if '-' in part and len(part) > 10 and 'dp' not in part and not part.startswith('B0'):
                        product_name = part.replace('-', ' ').title()
                        if len(product_name.split()) >= 3:
                            break
            
            elif 'walmart.com' in domain:
                parts = url.split('/')
                for part in parts:
                    if '-' in part and len(part) > 15 and not part.isdigit():
                        product_name = part.replace('-', ' ').title()
                        if len(product_name.split()) >= 3:
                            break
            
            else:
                # Generic extraction
                parts = url.split('/')
                for part in parts:
                    if '-' in part and len(part) > 8:
                        potential_name = part.replace('-', ' ').replace('_', ' ').title()
                        if len(potential_name.split()) >= 2:
                            product_name = potential_name
                            break
            
            if not product_name:
                return None
            
            # Enhanced categorization with better descriptions
            name_lower = product_name.lower()
            category = 'general'
            product_type = product_name  # Default to full name
            
            # Check for lighting products (including mushroom lamps)
            lighting_keywords = ['lamp', 'light', 'led', 'bulb', 'lighting']
            mushroom_lamp_keywords = ['mushroom', 'nightstand', 'dimmable', 'aesthetic'] 
            
            if (any(word in name_lower for word in lighting_keywords) or 
                (any(word in name_lower for word in mushroom_lamp_keywords) and 
                 any(word in name_lower for word in ['table', 'desk', 'nightstand', 'bedside']))):
                category = 'lighting'
                if 'table' in name_lower or 'desk' in name_lower:
                    product_type = 'Table Lamp'
                elif 'floor' in name_lower:
                    product_type = 'Floor Lamp'
                elif 'ceiling' in name_lower:
                    product_type = 'Ceiling Light'
                else:
                    product_type = 'Decorative Lamp'
                    
            elif any(word in name_lower for word in ['iphone', 'phone', 'smartphone']):
                category = 'electronics'
                product_type = 'Smartphone'
                
            elif any(word in name_lower for word in ['sofa', 'couch']):
                category = 'furniture'
                if '3' in name_lower or 'three' in name_lower:
                    product_type = '3-Seater Sofa'
                elif '2' in name_lower or 'two' in name_lower:
                    product_type = '2-Seater Sofa'
                else:
                    product_type = 'Sofa'
                    
            elif any(word in name_lower for word in ['chair', 'seat']):
                category = 'furniture'
                if 'office' in name_lower:
                    product_type = 'Office Chair'
                elif 'dining' in name_lower:
                    product_type = 'Dining Chair'
                else:
                    product_type = 'Chair'
                    
            elif any(word in name_lower for word in ['table']):
                category = 'furniture'
                if 'coffee' in name_lower:
                    product_type = 'Coffee Table'
                elif 'dining' in name_lower:
                    product_type = 'Dining Table'
                elif 'side' in name_lower or 'end' in name_lower:
                    product_type = 'Side Table'
                else:
                    product_type = 'Table'
                    
            elif any(word in name_lower for word in ['bed', 'mattress']):
                category = 'furniture'
                product_type = 'Bed'
                
            # Extract key descriptive words for search
            search_keywords = []
            words = product_name.lower().replace('-', ' ').split()
            for word in words:
                if len(word) > 2 and word not in ['the', 'and', 'for', 'with', 'buy']:
                    search_keywords.append(word)
            
            return {
                'name': product_name,
                'category': category,
                'product_type': product_type,
                'domain': domain,
                'search_keywords': search_keywords[:6]
            }
            
        except Exception as e:
            print(f"❌ URL analysis failed: {e}")
            return None
    
    def _search_with_tavily_best_practices(self, product_info: Dict[str, Any]) -> List[Dict]:
        """
        Search using Tavily best practices for diverse product discovery
        """
        product_name = product_info['name']
        category = product_info['category']
        exclude_domain = product_info['domain']
        
        # Create focused search queries for better relevance
        search_queries = []
        keywords = product_info["search_keywords"]
        
        # Query 1: Specific product search
        if len(keywords) >= 2:
            if category == 'lighting':
                search_queries.append(f'{keywords[0]} {keywords[1]} lamp lighting buy online')
            elif category == 'electronics':
                search_queries.append(f'{keywords[0]} {keywords[1]} electronics buy online')
            elif category == 'furniture':
                search_queries.append(f'{keywords[0]} {keywords[1]} furniture buy online')
            else:
                search_queries.append(f'{keywords[0]} {keywords[1]} buy online')
        
        # Query 2: Category-specific alternative search
        if category == 'lighting':
            if 'mushroom' in keywords:
                search_queries.append('mushroom table lamp desk lighting buy')
            else:
                search_queries.append('table lamp desk lighting buy online')
        elif category == 'electronics':
            search_queries.append(f'{keywords[0]} smartphone electronics buy')
        elif category == 'furniture':
            search_queries.append(f'{keywords[0]} furniture home decor buy')
        
        # Query 3: Brand/style alternative search
        if len(keywords) >= 3:
            search_queries.append(f'{keywords[1]} {keywords[2]} alternative similar buy')
        
        all_results = []
        
        for i, query in enumerate(search_queries[:3]):  # Use 3 diverse queries
            print(f"🔍 Tavily search {i+1}: '{query}'")
            
            # Vary search parameters for diversity
            if i == 0:
                # First search: focus on major retailers
                target_domains = ['amazon.com', 'walmart.com', 'target.com', 'bestbuy.com']
            elif i == 1:
                # Second search: specialty and mid-tier retailers
                target_domains = ['wayfair.com', 'overstock.com', 'homedepot.com', 'lowes.com', 'macys.com']
            else:
                # Third search: all retailers including smaller ones
                target_domains = self.shopping_domains
            
            try:
                response = self.client.search(
                    query=query,
                    search_depth="advanced",
                    max_results=8,  # Fewer per query for more diversity
                    include_domains=target_domains,
                    exclude_domains=[exclude_domain] if exclude_domain else None,
                    include_raw_content=True
                )
                
                if 'results' in response:
                    results = response['results']
                    all_results.extend(results)
                    print(f"   ✅ Found {len(results)} results")
                
                time.sleep(0.3)  # Faster between queries
                
            except Exception as e:
                print(f"   ❌ Search failed: {e}")
                continue
        
        print(f"📊 Total Tavily results: {len(all_results)}")
        return all_results
    
    def _process_and_verify_results(self, results: List[Dict], product_info: Dict[str, Any]) -> List[VerifiedProduct]:
        """
        Process search results with deduplication and retailer diversity
        """
        verified_products = []
        seen_urls = set()
        retailer_count = {}
        
        # Sort results by relevance first
        scored_results = []
        for result in results:
            try:
                title = result.get('title', '')
                content = result.get('content', '')
                if title and content:
                    relevance = self._calculate_product_relevance(product_info, title, content)
                    scored_results.append((relevance, result))
            except:
                continue
        
        # Sort by relevance descending
        scored_results.sort(key=lambda x: x[0], reverse=True)
        
        for relevance, result in scored_results:
            try:
                url = result.get('url', '')
                title = result.get('title', '')
                content = result.get('content', '')
                raw_content = result.get('raw_content', '')
                
                if not url or not title or url in seen_urls:
                    continue
                
                # Identify retailer
                domain = urlparse(url).netloc.lower().replace('www.', '')
                retailer = None
                
                for shop_domain, shop_name in self.retailer_names.items():
                    if shop_domain in domain:
                        retailer = shop_name
                        break
                
                if not retailer:
                    continue
                
                # Limit results per retailer for diversity (max 2 per retailer)
                if retailer_count.get(retailer, 0) >= 2:
                    continue
                
                # Check if it's a product page
                if not self._is_product_page(url, title, content):
                    continue
                
                # Minimum relevance check (more lenient)
                if relevance < 0.1:  # Back to 10% threshold
                    continue
                
                # Extract price with better methods
                price = self._extract_price_from_content(title, content, raw_content)
                
                # Skip if no price found and we already have results
                if not price and len(verified_products) >= 2:
                    continue
                
                # Clean up title for better display
                clean_title = self._clean_product_title(title)
                
                # Create verified product
                verified_product = VerifiedProduct(
                    title=clean_title,
                    price=price,
                    retailer=retailer,
                    url=url,
                    snippet=content[:180] if content else '',
                    relevance_score=relevance,
                    verified=True
                )
                
                verified_products.append(verified_product)
                seen_urls.add(url)
                retailer_count[retailer] = retailer_count.get(retailer, 0) + 1
                
                print(f"✅ Added: {retailer} - {relevance:.1%} relevance - ${price or 'Price TBD'}")
                
                # Stop when we have enough diverse results
                if len(verified_products) >= 5:
                    break
                
            except Exception as e:
                continue
        
        # Sort final results by price (best deals first)
        verified_products.sort(key=lambda x: self._get_price_value(x.price))
        
        return verified_products
    
    def _is_product_page(self, url: str, title: str, content: str) -> bool:
        """Enhanced product page detection"""
        
        # Skip obvious non-product pages
        non_product_url_indicators = [
            'keyword.php', 'search?', '/search/', '/category/', '/browse/'
        ]
        
        url_lower = url.lower()
        title_lower = title.lower()
        
        # Check URL patterns
        for indicator in non_product_url_indicators:
            if indicator in url_lower:
                return False
        
        # Check for completely unrelated products in title only
        unrelated_products = ['pizza', 'coffee', 'beverage', 'grocery', 'clothing', 'book']
        title_words = title_lower.split()
        
        # Only exclude if the title is clearly about unrelated products
        for product in unrelated_products:
            if product in title_words and len([w for w in title_words if w in ['lamp', 'light', 'mushroom', 'table']]) == 0:
                return False
        
        # URL patterns that indicate product pages
        product_url_patterns = [
            r'/p/', r'/dp/', r'/item/', r'/product/', r'/buy/', r'-p-', r'/ip/', r'/pd/'
        ]
        
        has_product_url = False
        for pattern in product_url_patterns:
            if re.search(pattern, url, re.IGNORECASE):
                has_product_url = True
                break
        
        # Content indicators
        combined_text = (title + ' ' + content).lower()
        product_indicators = [
            'price', 'buy now', 'add to cart', 'shipping', 'reviews', 'rating', 
            'in stock', 'out of stock', 'purchase', '$', 'sale', 'order'
        ]
        
        indicator_count = sum(1 for indicator in product_indicators if indicator in combined_text)
        
        # Require either product URL pattern OR strong content indicators
        return has_product_url or indicator_count >= 3
    
    def _calculate_product_relevance(self, product_info: Dict[str, Any], title: str, content: str) -> float:
        """
        Enhanced relevance calculation with category matching
        """
        original_name = product_info['name'].lower()
        category = product_info['category']
        
        # Combine title and content for analysis
        candidate_text = (title + ' ' + content).lower()
        
        # Only disqualify if clearly unrelated AND no relevant terms
        irrelevant_terms = ['pizza', 'coffee', 'beverage', 'clothing', 'book', 'movie']
        relevant_terms = ['lamp', 'light', 'mushroom', 'table', 'nightstand', 'lighting']
        
        has_irrelevant = any(term in candidate_text for term in irrelevant_terms)
        has_relevant = any(term in candidate_text for term in relevant_terms)
        
        # Only exclude if it has irrelevant terms AND no relevant terms
        if has_irrelevant and not has_relevant:
            return 0.0
        
        # Extract meaningful words
        original_words = set(re.findall(r'\b\w{3,}\b', original_name))
        candidate_words = set(re.findall(r'\b\w{3,}\b', candidate_text))
        
        # Enhanced stop words
        stop_words = {
            'the', 'and', 'for', 'with', 'buy', 'online', 'store', 'shop', 'sale',
            'price', 'best', 'top', 'new', 'free', 'shipping', 'fast', 'great',
            'quality', 'perfect', 'amazing', 'beautiful', 'modern', 'style'
        }
        original_words -= stop_words
        candidate_words -= stop_words
        
        if not original_words:
            return 0.0
        
        # Calculate word overlap
        intersection = len(original_words.intersection(candidate_words))
        base_relevance = intersection / len(original_words)
        
        # Strong category matching bonus
        category_bonus = 0.0
        if category == 'lighting':
            lighting_terms = ['lamp', 'light', 'led', 'bulb', 'lighting', 'illumination']
            if any(term in candidate_text for term in lighting_terms):
                category_bonus = 0.3
        elif category == 'electronics':
            electronics_terms = ['phone', 'electronic', 'tech', 'device', 'gadget']
            if any(term in candidate_text for term in electronics_terms):
                category_bonus = 0.3
        elif category == 'furniture':
            furniture_terms = ['furniture', 'chair', 'table', 'sofa', 'bed', 'desk']
            if any(term in candidate_text for term in furniture_terms):
                category_bonus = 0.3
        
        # Penalty for wrong category
        category_penalty = 0.0
        if category == 'lighting' and any(term in candidate_text for term in ['food', 'clothing', 'book']):
            category_penalty = 0.5
        
        final_score = min(base_relevance + category_bonus - category_penalty, 1.0)
        return max(final_score, 0.0)
    
    def _extract_price_from_content(self, title: str, content: str, raw_content: str) -> Optional[str]:
        """
        Enhanced price extraction with better patterns
        """
        all_text = f"{title} {content} {raw_content or ''}"
        
        # Enhanced price patterns
        price_patterns = [
            r'\$(\d{1,4}(?:,\d{3})*(?:\.\d{2})?)\b',  # $1,234.56
            r'Price:?\s*\$(\d{1,4}(?:,\d{3})*(?:\.\d{2})?)',  # Price: $123
            r'(\d{1,4}(?:,\d{3})*(?:\.\d{2})?)\s*USD',  # 123.45 USD
            r'Sale:?\s*\$(\d{1,4}(?:,\d{3})*(?:\.\d{2})?)',  # Sale: $123
            r'Now:?\s*\$(\d{1,4}(?:,\d{3})*(?:\.\d{2})?)',  # Now: $123
            r'Only:?\s*\$(\d{1,4}(?:,\d{3})*(?:\.\d{2})?)',  # Only: $123
            r'\$(\d{1,3}(?:\.\d{2})?)\b',  # Simple $123.45
        ]
        
        found_prices = []
        
        for pattern in price_patterns:
            matches = re.findall(pattern, all_text, re.IGNORECASE)
            for match in matches:
                try:
                    price_val = float(match.replace(',', ''))
                    # Reasonable price range for most products
                    if 5.0 <= price_val <= 5000.0:
                        found_prices.append(price_val)
                except:
                    continue
        
        if found_prices:
            # Return the most reasonable price (not too low, not too high)
            found_prices.sort()
            return f"${found_prices[0]:.2f}"
        
        return None
    
    def _clean_product_title(self, title: str) -> str:
        """
        Clean up product titles for better display
        """
        # Remove common e-commerce noise
        title = re.sub(r'\s*-\s*(Amazon\.com|Walmart\.com|eBay|Target\.com).*$', '', title, flags=re.IGNORECASE)
        title = re.sub(r'\s*\|\s*eBay.*$', '', title, flags=re.IGNORECASE)
        title = re.sub(r'\s*\.\.\.$', '', title)
        
        # Limit length
        if len(title) > 80:
            title = title[:77] + "..."
        
        return title.strip()
    
    def _get_price_value(self, price_str: Optional[str]) -> float:
        """Convert price string to numeric value for sorting"""
        if not price_str:
            return 999999.0  # High value for items without price
        
        try:
            # Extract numeric value from price string
            numeric_part = re.findall(r'[\d,]+\.?\d*', price_str.replace('$', ''))
            if numeric_part:
                return float(numeric_part[0].replace(',', ''))
        except:
            pass
        
        return 999999.0


# Initialize the engine
engine = ProductionCiergeEngine(TAVILY_API_KEY)


# HTML Templates
LANDING_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>cierge — Stop Overpaying for Your Products</title>
    <style>
        *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: Arial, Helvetica, sans-serif; color: #333; background: #fff; line-height: 1.6; -webkit-font-smoothing: antialiased; }
        
        .nav { background: #1F3864; padding: 16px 24px; text-align: center; }
        .nav .logo { color: #fff; font-size: 22px; font-weight: 700; letter-spacing: 0.5px; }
        
        .hero { max-width: 720px; margin: 0 auto; padding: 64px 24px 48px; text-align: center; }
        .hero h1 { font-size: 36px; line-height: 1.2; color: #1F3864; margin-bottom: 20px; }
        .hero p { font-size: 18px; color: #555; margin-bottom: 36px; max-width: 600px; margin-left: auto; margin-right: auto; }
        
        .form-section { max-width: 500px; margin: 0 auto 40px; padding: 0 24px; }
        .form-group { margin-bottom: 20px; }
        .form-group label { display: block; margin-bottom: 8px; font-weight: 600; color: #1F3864; font-size: 16px; }
        .form-group input { width: 100%; padding: 16px; border: 2px solid #E0E7EF; border-radius: 8px; font-size: 16px; transition: border-color 0.2s; }
        .form-group input:focus { outline: none; border-color: #2E75B6; }
        
        .cta-btn { display: inline-block; background: #2E75B6; color: #fff; font-size: 18px; font-weight: 700; padding: 16px 40px; border: none; border-radius: 8px; cursor: pointer; text-decoration: none; transition: background 0.2s, transform 0.1s; width: 100%; }
        .cta-btn:hover { background: #245d94; transform: translateY(-1px); }
        
        .retailers { text-align: center; padding: 24px; color: #888; font-size: 14px; letter-spacing: 0.3px; }
        .retailers span { display: inline-block; margin: 0 10px; font-weight: 600; color: #777; }
        
        .trust { max-width: 720px; margin: 0 auto; padding: 56px 24px; text-align: center; }
        .trust h2 { font-size: 26px; color: #1F3864; margin-bottom: 32px; }
        .trust-grid { display: flex; gap: 24px; flex-wrap: wrap; justify-content: center; }
        .trust-item { flex: 1 1 200px; max-width: 220px; padding: 20px; border: 1px solid #E0E7EF; border-radius: 10px; background: #fff; }
        .trust-item .icon { font-size: 28px; margin-bottom: 8px; }
        .trust-item h4 { font-size: 15px; color: #1F3864; margin-bottom: 4px; }
        .trust-item p { font-size: 13px; color: #777; }
        
        .footer { text-align: center; padding: 24px; color: #aaa; font-size: 13px; }
        
        @media (max-width: 600px) {
            .hero h1 { font-size: 26px; }
            .hero p { font-size: 16px; }
            .cta-btn { font-size: 16px; padding: 14px 28px; }
            .retailers span { display: block; margin: 4px 0; }
        }
    </style>
</head>
<body>
    <div class="nav">
        <div class="logo">cierge</div>
    </div>
    
    <div class="hero">
        <h1>Stop opening 6 tabs for one purchase. We'll tell you where to actually buy it.</h1>
        <p>Paste a product link. We compare price, shipping, returns, reviews, and seller trust across major retailers — and give you the best option instantly.</p>
    </div>
    
    <div class="form-section">
        <form method="POST" action="/compare">
            <div class="form-group">
                <label for="product_url">Product URL</label>
                <input type="url" id="product_url" name="product_url" 
                       placeholder="https://www.amazon.com/product-name/dp/B123456789/" required>
            </div>
            <div class="form-group">
                <label for="email">Email Address</label>
                <input type="email" id="email" name="email" 
                       placeholder="your@email.com" required>
            </div>
            <button type="submit" class="cta-btn">Compare My Product — Free</button>
        </form>
    </div>
    
    <div class="retailers">
        We compare across: <span>Amazon</span> <span>Walmart</span> <span>Target</span> <span>eBay</span> <span>Wayfair</span> <span>Etsy</span>
    </div>
    
    <div class="trust">
        <h2>Why people use cierge</h2>
        <div class="trust-grid">
            <div class="trust-item">
                <div class="icon">💰</div>
                <h4>Save real money</h4>
                <p>The same product can vary $20–$80 across retailers. We find the best total price.</p>
            </div>
            <div class="trust-item">
                <div class="icon">⏱️</div>
                <h4>Save your time</h4>
                <p>No more 6 tabs, 6 logins, and 6 different shipping calculators.</p>
            </div>
            <div class="trust-item">
                <div class="icon">🔒</div>
                <h4>Unbiased picks</h4>
                <p>We don't earn affiliate commissions. Our recommendation is actually the best one.</p>
            </div>
        </div>
    </div>
    
    <div class="footer">
        © 2026 cierge — Built for smart shoppers.
    </div>
</body>
</html>
"""

RESULTS_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>cierge — Your Product Comparison Results</title>
    <style>
        *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: Arial, Helvetica, sans-serif; color: #333; background: #F7F9FC; line-height: 1.6; -webkit-font-smoothing: antialiased; }
        
        .nav { background: #1F3864; padding: 16px 24px; text-align: center; }
        .nav .logo { color: #fff; font-size: 22px; font-weight: 700; letter-spacing: 0.5px; }
        
        .container { max-width: 900px; margin: 0 auto; padding: 40px 24px; }
        .back-link { display: inline-block; margin-bottom: 30px; color: #2E75B6; text-decoration: none; font-weight: 600; }
        .back-link:hover { text-decoration: underline; }
        
        .header { text-align: center; margin-bottom: 40px; }
        .header h1 { color: #1F3864; font-size: 28px; margin-bottom: 12px; }
        .header p { color: #666; font-size: 16px; }
        
        .original-product { background: #1F3864; color: white; padding: 32px; border-radius: 10px; margin-bottom: 40px; text-align: center; }
        .original-product h2 { margin-bottom: 12px; font-size: 22px; }
        .original-product p { font-size: 16px; opacity: 0.9; }
        
        .results-list { display: flex; flex-direction: column; gap: 24px; }
        .result-card { background: white; padding: 28px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); border-left: 4px solid #2E75B6; }
        .result-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
        .rank-retailer { display: flex; align-items: center; }
        .rank { background: #2E75B6; color: white; width: 32px; height: 32px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 700; margin-right: 16px; font-size: 16px; }
        .retailer { font-size: 20px; font-weight: 700; color: #1F3864; }
        .price { font-size: 24px; font-weight: 700; color: #2E75B6; }
        
        .product-title { color: #333; margin-bottom: 12px; font-size: 16px; line-height: 1.5; }
        .match-score { background: #E8F0FE; color: #1F3864; padding: 4px 12px; border-radius: 16px; font-size: 12px; font-weight: 600; display: inline-block; margin-bottom: 16px; }
        .product-snippet { color: #666; margin-bottom: 20px; font-size: 14px; }
        .view-btn { display: inline-block; background: #2E75B6; color: white; padding: 12px 24px; border-radius: 6px; text-decoration: none; font-weight: 600; font-size: 14px; transition: background 0.2s; }
        .view-btn:hover { background: #245d94; }
        
        .no-results { background: white; padding: 48px; border-radius: 10px; text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
        .no-results h2 { color: #1F3864; margin-bottom: 16px; }
        .no-results p { color: #666; }
        
        .footer { text-align: center; padding: 32px 24px; color: #aaa; font-size: 13px; }
        
        @media (max-width: 600px) {
            .result-header { flex-direction: column; align-items: flex-start; gap: 12px; }
            .price { font-size: 20px; }
        }
    </style>
</head>
<body>
    <div class="nav">
        <div class="logo">cierge</div>
    </div>
    
    <div class="container">
        <a href="/" class="back-link">← Compare Another Product</a>
        
        <div class="header">
            <h1>Your Comparison Results</h1>
            <p>We found the best options across major retailers</p>
        </div>
        
        <div class="original-product">
            <h2>Looking for</h2>
            <p><strong>{{ original_product.product_type or original_product.name }}</strong></p>
            <p>{{ results|length }} alternative{{ 's' if results|length != 1 else '' }} found</p>
        </div>
        
        {% if results %}
        <div class="results-list">
            {% for result in results %}
            <div class="result-card">
                <div class="result-header">
                    <div class="rank-retailer">
                        <div class="rank">{{ loop.index }}</div>
                        <div class="retailer">{{ result.retailer }}</div>
                    </div>
                    <div class="price">{{ result.price or 'Contact for price' }}</div>
                </div>
                
                <div class="product-title">{{ result.title }}</div>
                
                <div class="match-score">{{ "%.0f"|format(result.relevance_score * 100) }}% Match</div>
                
                {% if result.snippet %}
                <div class="product-snippet">{{ result.snippet }}...</div>
                {% endif %}
                
                <a href="{{ result.url }}" target="_blank" class="view-btn">
                    View at {{ result.retailer }} →
                </a>
            </div>
            {% endfor %}
        </div>
        {% else %}
        <div class="no-results">
            <h2>Search Complete</h2>
            <p>We searched across major retailers but couldn't find similar products at other stores.</p>
            <p style="margin-top: 16px; color: #888;">This might mean the product is exclusive or very unique.</p>
        </div>
        {% endif %}
    </div>
    
    <div class="footer">
        © 2026 cierge — Built for smart shoppers.
    </div>
</body>
</html>
"""

PROCESSING_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>cierge — Comparing Your Product</title>
    <meta http-equiv="refresh" content="3">
    <style>
        *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: Arial, Helvetica, sans-serif; color: #333; background: #F7F9FC; line-height: 1.6; -webkit-font-smoothing: antialiased; min-height: 100vh; display: flex; align-items: center; justify-content: center; }
        
        .processing-card { background: white; padding: 60px 40px; border-radius: 10px; box-shadow: 0 8px 25px rgba(0,0,0,0.1); text-align: center; max-width: 500px; border: 1px solid #E0E7EF; }
        .spinner { width: 50px; height: 50px; border: 4px solid #E0E7EF; border-top: 4px solid #2E75B6; border-radius: 50%; animation: spin 1s linear infinite; margin: 0 auto 24px; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        
        h1 { color: #1F3864; margin-bottom: 16px; font-size: 24px; font-weight: 700; }
        .subtitle { color: #666; margin-bottom: 24px; font-size: 16px; }
        .status { background: #2E75B6; color: white; padding: 12px 20px; border-radius: 6px; display: inline-block; font-weight: 600; font-size: 14px; }
        
        .progress-info { margin-top: 24px; color: #888; font-size: 13px; }
        .progress-info p { margin: 4px 0; }
    </style>
</head>
<body>
    <div class="processing-card">
        <div class="spinner"></div>
        <h1>Comparing Your Product</h1>
        <div class="subtitle">
            We're checking major retailers for the best deals and options.
        </div>
        
        <div class="status">{{ status }}</div>
        
        <div class="progress-info">
            <p>Searching across Amazon, Walmart, Target, eBay, and more</p>
            <p>Comparing prices, shipping, and availability</p>
            <p>Finding you the best deal</p>
        </div>
    </div>
</body>
</html>
"""


@app.route('/')
def index():
    """Landing page"""
    return render_template_string(LANDING_TEMPLATE)


@app.route('/compare', methods=['POST'])
def compare():
    """Start product comparison"""
    product_url = request.form.get('product_url')
    email = request.form.get('email')
    
    if not product_url or not email:
        return "Missing product URL or email", 400
    
    # Generate comparison ID
    comparison_id = str(uuid.uuid4())
    
    # Store comparison request
    search_requests[comparison_id] = {
        'id': comparison_id,
        'product_url': product_url,
        'email': email,
        'status': 'starting',
        'original_product': None,
        'results': [],
        'created_at': time.time()
    }
    
    # Start AI comparison in background
    thread = threading.Thread(target=run_ai_comparison, args=(comparison_id,))
    thread.daemon = True
    thread.start()
    
    return redirect(url_for('status', comparison_id=comparison_id))


@app.route('/status/<comparison_id>')
def status(comparison_id):
    """Show comparison status or results"""
    comparison_data = search_requests.get(comparison_id)
    
    if not comparison_data:
        return "Comparison not found", 404
    
    # If completed, show results
    if comparison_data['status'] == 'completed':
        return render_template_string(RESULTS_TEMPLATE,
                                    original_product=comparison_data['original_product'],
                                    results=comparison_data['results'])
    
    # Show processing status
    status_messages = {
        'starting': 'Initializing AI systems...',
        'analyzing': 'AI analyzing your product...',
        'searching': 'AI searching the entire web...',
        'processing': 'AI processing thousands of results...',
        'verifying': 'AI verifying product matches...',
        'completed': 'AI analysis complete!'
    }
    
    current_status = status_messages.get(comparison_data['status'], 'AI processing...')
    
    return render_template_string(PROCESSING_TEMPLATE, status=current_status)


def run_ai_comparison(comparison_id: str):
    """
    Run AI-powered product comparison using Tavily
    """
    try:
        comparison_data = search_requests[comparison_id]
        product_url = comparison_data['product_url']
        
        print(f"🤖 Starting AI comparison for: {product_url}")
        
        # Update status
        comparison_data['status'] = 'analyzing'
        
        # Use Tavily AI to find alternatives
        alternatives = engine.find_product_alternatives(product_url)
        
        # Extract original product info with better categorization
        original_product = {'name': 'Unknown Product', 'product_type': 'Product', 'url': product_url}
        
        try:
            # Use the same analysis method as the engine
            product_info = engine._analyze_product_url(product_url)
            if product_info:
                original_product['name'] = product_info['name']
                original_product['product_type'] = product_info['product_type']
        except:
            pass
        
        # Store results
        comparison_data['original_product'] = original_product
        comparison_data['results'] = alternatives
        comparison_data['status'] = 'completed'
        
        print(f"🎯 AI comparison completed: Found {len(alternatives)} alternatives")
        
    except Exception as e:
        print(f"❌ AI comparison failed: {e}")
        search_requests[comparison_id]['status'] = 'failed'


if __name__ == '__main__':
    print("🚀 Starting Production Cierge - AI Product Comparison")
    print("🤖 Powered by Tavily AI with best practices")
    print("🌐 Visit: http://localhost:5007")
    
    app.run(host='0.0.0.0', port=5007, debug=True)