from application import app
from application.database import db, redis_db
from application.models.model import CryptoCurrency
from application.controllers.helpers import get_current_timestamp, timestamp_to_datetime
from application.config import Config
import requests
import ujson


def get_current_coin_price(coin_id, currency="usd"):
    url = Config.API_COIN + f"/simple/price?ids={coin_id}&vs_currencies={currency}"
    response = requests.get(url)
    if response.status_code == 200:
        resp_dict = response.json()
        curr_price = resp_dict.get(coin_id).get(currency)
        curr_timestamp = get_current_timestamp()
        result = {
            "time_stamp": curr_timestamp,
            "price": curr_price,
            "datetime": timestamp_to_datetime(curr_timestamp),
        }
        return result
    else:
        raise Exception("Lỗi api coin")


def cache_coin_prices(coin_id=None, recent_prices=None, current_price=None):
    """Lưu giá vào redis"""
    if not recent_prices:
        new_prices = []
        new_prices.append(current_price)
        redis_db.set(coin_id, ujson.dumps(new_prices))
    else:
        recent_prices = ujson.loads(recent_prices)
        if len(recent_prices) < 50:
            recent_prices.append(current_price)
            redis_db.set(coin_id, ujson.dumps(recent_prices))
        if len(recent_prices) >= 50:
            recent_prices.pop(0)
            recent_prices.append(current_price)
            redis_db.set(coin_id, ujson.dumps(recent_prices))


def sync_recent_price():
    """Đồng bộ giá của các coin được theo dõi rồi cache vào redis
    Tối đa 50 record trên 1 coin, 5 phút một lần
    """
    followed_coins = (
        db.session.query(CryptoCurrency).filter(CryptoCurrency.is_follow == True).all()
    )

    for coin in followed_coins:
        coin_id = coin.gecko_coin_id
        coin_curren_price = get_current_coin_price(coin_id=coin_id)
        coin_recent_prices = redis_db.get(coin_id)
        cache_coin_prices(
            coin_id=coin_id,
            recent_prices=coin_recent_prices,
            current_price=coin_curren_price,
        )
