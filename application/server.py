""" App entry point. """

from gatco import Gatco
from gatco.sessions import CookieSessionInterface
from .config import Config
from sanic_cors import CORS

app = Gatco(name=__name__)
app.session_interface = CookieSessionInterface()  # type: ignore
app.config.from_object(Config)
CORS(app, automatic_options=True)

from application.database import init_database
from application.extensions import init_extensions
from application.controllers import init_views

static_endpoint = app.config.get("STATIC_URL", None)
if (static_endpoint is not None) and not (
    (static_endpoint.startswith("http://") or (static_endpoint.startswith("https://")))
):
    app.static(static_endpoint, "./static")

init_database(app)
init_extensions(app)
init_views(app)
