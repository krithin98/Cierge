#!/usr/bin/env python3
"""
WSGI entry point for Render deployment
"""

import os
from production_ready_app import app, ProductionCiergeEngine

# Initialize engine with environment variable
TAVILY_API_KEY = os.environ.get('TAVILY_API_KEY', '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')

# Create new engine instance
engine = ProductionCiergeEngine(TAVILY_API_KEY)

# Replace the global engine in the module
import production_ready_app
production_ready_app.engine = engine

# Export the app for WSGI servers
application = app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5007))
    print(f"🚀 Starting Cierge on port {port}")
    print(f"🔑 API Key configured: {'✅' if TAVILY_API_KEY else '❌'}")
    app.run(host="0.0.0.0", port=port, debug=False)