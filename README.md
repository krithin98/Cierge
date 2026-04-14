# 🎯 Cierge - AI Product Comparison

AI-powered product comparison tool that finds the best deals across the web using Tavily search API.

## Features

- 🤖 **AI-Powered Search**: Uses Tavily API for intelligent web search
- 🌐 **Web-Wide Coverage**: Searches across Amazon, Walmart, Target, eBay, Wayfair, and more
- 🎯 **Smart Matching**: AI relevance scoring finds truly similar products
- 💰 **Real Prices**: Extracts actual prices from retailer websites
- ⚡ **Fast Results**: Get alternatives in under 30 seconds
- 📱 **Modern UI**: Beautiful, responsive interface

## Quick Start

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd cierge-v3
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set environment variables**
```bash
export TAVILY_API_KEY=your_tavily_api_key_here
```

4. **Run the app**
```bash
python app.py
```

Visit `http://localhost:5007` to use the app.

## Deployment

### Render (Free)
1. Connect your GitHub repo to Render
2. Set environment variable: `TAVILY_API_KEY`
3. Deploy automatically

### Railway (Free tier)
1. Connect GitHub repo to Railway
2. Set environment variable: `TAVILY_API_KEY`
3. Deploy with one click

## API Key

Get your free Tavily API key at [tavily.com](https://tavily.com)

## Tech Stack

- **Backend**: Python Flask
- **Search**: Tavily API
- **Web Scraping**: BeautifulSoup4, Requests
- **Frontend**: HTML/CSS (embedded templates)

## License

MIT License