import os
from .server import app
from sanic.websocket import WebSocketProtocol 

def run_app(host="127.0.0.1", port=8000, debug=False):
    """ Function for bootstrapping gatco app. """
    app.run(host=host, port=port, debug=debug, workers=os.cpu_count(), protocol=WebSocketProtocol)

