from application.controllers.helpers import to_dict
from application.models.model import CryptoCurrency
from application.extensions import apimanager
from application.controllers import auth_func
from application.server import app
from sanic.response import json
from application.database import db

apimanager.create_api(
    collection_name="crypto_currency",
    model=CryptoCurrency,
    methods=["GET", "POST", "DELETE", "PUT"],
    url_prefix="/api/v1",
    preprocess=dict(
        GET_SINGLE=[auth_func],
        GET_MANY=[auth_func],
        POST=[auth_func],
        PUT_SINGLE=[auth_func],
    ),
)


@app.route("/search_coin", methods=["GET"])
async def handle_search_coin(request):
    if request.method == "GET":
        search_options = request.args.get("search_options")
        size = request.args.get("size")
        if int(size) > 50:
            return json({"error": "Size too big"}, 400)
        search_options = search_options.split(",")
        search = (
            "%" + request.args.get("search") + "%"
            if "find_extract" not in search_options
            else request.args.get("search")
        )
        print("search", search)
        query = db.session.query(CryptoCurrency)
        if "find_by_id" in search_options:
            if "find_extract" in search_options:
                query = query.filter(CryptoCurrency.gecko_coin_id == search)
            else:
                query = query.filter(CryptoCurrency.gecko_coin_id.ilike(search))
        if "find_by_symbol" in search_options:
            if "find_extract" in search_options:
                query = query.filter(CryptoCurrency.symbol == search)
            else:
                query = query.filter(CryptoCurrency.symbol.ilike(search))
        print(query)

        records = query.limit(int(size)).all()

        results = [to_dict(result) for result in records]
        return json(results)
