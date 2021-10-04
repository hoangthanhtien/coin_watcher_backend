from application.server import app
from application.database import redis_db
from sanic.response import HTTPResponse, json
from application.models.model import CryptoPrice
from application.extensions import apimanager
from application.controllers import auth_func
from application.config import Config
import ujson


@app.route("/current_price", methods=["GET"])
async def get_current_price(request):
    coin_id = request.args.get("coin_id")
    if not coin_id:
        return json({}, 400)
    key = coin_id + "_now"
    print(key)
    price = (redis_db.get(key)).decode("utf-8")
    return json({"price": price})


@app.route("/recent_prices", methods=["GET"])
async def get_recent_prices(request):
    if request.method == "GET":
        response = auth_func(request=request)
        print("response", isinstance(response, HTTPResponse))
        if isinstance(response, HTTPResponse):
            return response
        coin_ids = request.args.get("coin_ids")
        if not coin_ids or coin_ids == "":
            return json(Config.BAD_REQUEST_ERR, 400)
        coin_ids = coin_ids.split(",")
        result = {}
        for coin_id in coin_ids:
            coin_price_info = redis_db.get(coin_id)
            if not coin_price_info:
                return json(
                    {
                        "error": f"id {coin_id} không tồn tại trên hệ thống hoặc chưa được theo dõi giá"
                    },
                    404,
                )
            else:
                result[coin_id] = ujson.loads(coin_price_info)
        return json(result, 200)


apimanager.create_api(
    collection_name="crypto_price",
    model=CryptoPrice,
    methods=["GET", "POST", "DELETE", "PUT"],
    url_prefix="/api/v1",
    preprocess=dict(
        GET_SINGLE=[],
        GET_MANY=[],
        POST=[auth_func],
        PUT_SINGLE=[auth_func],
    ),
)
