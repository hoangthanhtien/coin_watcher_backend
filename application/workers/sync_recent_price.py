from application import app
from application.database import db, redis_db
from application.models.model import CryptoCurrency, Notification
from application.controllers.helpers import (
    get_current_timestamp,
    timestamp_to_datetime,
    send_email,
    to_dict,
)
from application.config import Config
from sqlalchemy import and_
import requests
import ujson
import asyncio
import traceback


def convert_number_to_4_digits(num):
    if num <= 9999.9999 and num >= 1000:
        string = "{:04d}".format(int(num))
        return string
    if num <= 999.9999 and num >= 100:
        string = "{0:.1f}".format(num)
        return string
    if num <= 99.9999 and num >= 10:
        string = "{0:.2f}".format(num)
        return string
    if num <= 9.9999 and num >= 1:
        string = "{0:.3f}".format(num)
        return string
    if num < 0.9999 and num > 0:
        string = "{0:.3f}".format(num)
        return string
    return 9999


def cache_current_price(coin_id, price):
    redis_db.set(coin_id, convert_number_to_4_digits(num=price))


def check_notification(coin_id, coin_curren_price):
    """Kiểm tra xem có user nào đặt thông báo tại mức giá này hay không
    :param str coin_id: Mã gecko_coin_id
    :param float coin_curren_price: Giá coin hiện tại
    """
    notification_records = (
        db.session.query(Notification)
        .filter(and_(Notification.coin_id == coin_id, Notification.is_notify == False))
        .all()
    )

    for noti in notification_records:
        noti_types = str(noti.notify_type).split(",")
        price_status = noti.price_status
        notify_price = float(noti.notify_price_at)
        user_info = to_dict(noti.user)
        # print(noti_types, price_status, notify_price, user_info, coin_curren_price)

        if "0" in noti_types:
            # Noti nếu giá hiện hành nhỏ hơn hoặc bằng giá cài đặt để thông báo
            if price_status == 0:
                print(noti_types)
                print(to_dict(noti))
                if coin_curren_price.get("price") <= notify_price:
                    data = {
                        "price": coin_curren_price.get("price"),
                        "coin_id": to_dict(noti.coin).get("gecko_coin_id"),
                    }
                    loop = asyncio.get_event_loop()
                    try:
                        loop.run_until_complete(
                            asyncio.gather(
                                send_email(
                                    to_email_addresses=[user_info.get("email")],
                                    mail_content_type="notify_price",
                                    additional_data=data,
                                ),
                            )
                        )
                    except Exception:
                        exept_txt = traceback.format_exc()
                        print("exept_txt", exept_txt)
                    finally:
                        noti.is_notify = True
                        db.session.commit()
                        loop.close()

            # Noti nếu giá hiện hành lớn hơn hoặc bằng giá cài đặt để thông báo
            if price_status == 1:
                print(price_status)
                print(to_dict(noti))
                if coin_curren_price.get("price") >= notify_price:
                    data = {
                        "price": coin_curren_price.get("price"),
                        "coin_id": to_dict(noti.coin).get("gecko_coin_id"),
                    }
                    loop = asyncio.get_event_loop()
                    try:
                        loop.run_until_complete(
                            asyncio.gather(
                                send_email(
                                    to_email_addresses=[user_info.get("email")],
                                    mail_content_type="notify_price",
                                    additional_data=data,
                                ),
                            )
                        )
                    except Exception:
                        exept_txt = traceback.format_exc()
                        print("exept_txt", exept_txt)
                    finally:
                        noti.is_notify = True
                        db.session.commit()
                        loop.close()
                    data = {
                        "price": notify_price,
                        "coin_id": to_dict(noti.coin).get("gecko_coin_id"),
                    }


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
    cache_current_price(coin_id, current_price.get("price"))
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
        coin_primary_key = coin.id
        coin_curren_price = get_current_coin_price(coin_id=coin_id)
        coin_recent_prices = redis_db.get(coin_id)
        cache_coin_prices(
            coin_id=coin_id,
            recent_prices=coin_recent_prices,
            current_price=coin_curren_price,
        )
        check_notification(
            coin_id=coin_primary_key, coin_curren_price=coin_curren_price
        )
