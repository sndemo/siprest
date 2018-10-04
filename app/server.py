import os
import sys
import logging
from aiohttp import web

from web import app
from web.config import config
from web import route

# Add web to python library path
sys.path.append(os.path.join(os.path.dirname(__file__), "web"))

if __name__ == "__main__":
  logging.basicConfig(level=logging.DEBUG)
  app = web.Application()
  app.add_routes(route.routes)
  web.run_app(app)
