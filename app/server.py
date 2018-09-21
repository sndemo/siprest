import os
import sys
import logging
from elasticsearch_dsl.connections import connections
from aiohttp import web

from web import app
from web.config import config
from web import route

# Add web to python library path
sys.path.append(os.path.join(os.path.dirname(__file__), "web"))

# Define a default Elasticsearch client
connections.create_connection(hosts=['elasticsearch'])

if __name__ == "__main__":
  logging.basicConfig(level=logging.DEBUG)
  app = web.Application()
  app.add_routes(route.routes)
  web.run_app(app)
