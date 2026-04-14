#!/usr/bin/env python3
"""
Cierge - Production deployment version
"""

import os
from production_ready_app import app, engine

# Use environment variable for API key in production
if 'TAVILY_API_KEY' in os.environ:
    engine.client.api_key = os.environ['TAVILY_API_KEY']

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5007))
    app.run(host='0.0.0.0', port=port, debug=False)