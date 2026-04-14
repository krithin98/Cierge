# Product Comparison with Tavily Search

This skill enables AI agents to perform intelligent product comparison by:
1. Analyzing product URLs to extract product details
2. Using Tavily API to search the web for the same/similar products
3. Filtering results to find actual shopping sites
4. Verifying URLs work and extracting real prices
5. Ranking results by price, shipping, and retailer trust

## Usage

The skill provides a complete product comparison workflow:

```python
# Example usage
from product_comparison_skill import ProductComparisonEngine

engine = ProductComparisonEngine(tavily_api_key="your-key")

# User provides any product URL
product_url = "https://www.amazon.com/product-name/dp/B123456789/"

# Get 5 best alternative options
results = engine.find_best_alternatives(product_url)

# Results include:
# - Real product titles
# - Real prices  
# - Real working URLs
# - Retailer information
# - Similarity scores
```

## Features

- ✅ **Real Web Search**: Uses Tavily API for live web search
- ✅ **Smart Product Analysis**: Extracts product details from any URL
- ✅ **URL Verification**: Ensures all returned links actually work
- ✅ **Price Extraction**: Gets real current prices
- ✅ **Intelligent Filtering**: Only returns actual shopping sites
- ✅ **Ranking Algorithm**: Sorts by price, shipping, retailer trust

## Installation

```bash
pip install tavily-python beautifulsoup4 requests
```

## API Key

Get your Tavily API key from: https://app.tavily.com

## Integration

This skill integrates with:
- Cursor AI
- Claude Code
- Any Python-based AI agent
- Flask/Django web applications
- Jupyter notebooks

The skill is designed to replace complex web scraping with reliable API calls while maintaining the intelligence needed for accurate product matching.