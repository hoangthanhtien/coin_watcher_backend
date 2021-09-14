from application.server import app
from application.database import db, redis_db
from sanic.response import json


@app.route("/recent_prices", methods=["GET"])
async def get_recent_prices(request):
    if request.method == "GET":
        return json({"hello_word": "Tien"})
