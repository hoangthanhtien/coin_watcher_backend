from application import app
from application.database import db
from datetime import date, timedelta
from application.config import Config
from application.models.model import CryptoPrice, CryptoCurrency, Currency
from application.controllers.helpers import (
    convert_datestring_to_timestamp,
    to_dict,
    timestamp_to_date,
)
import requests
import time
from sqlalchemy import and_


def get_dates_between(start_date, end_date):
    """Lấy thông tin các ngày giữa hai ngày
    :param str start_date: Ngày bắt đầu dd-mm-yyyy
    :param str end_date: Ngày kết thúc dd-mm-yyyy
    """
    start_date_value = start_date.split("-")
    end_date_value = end_date.split("-")
    sdate = date(
        int(start_date_value[2]), int(start_date_value[1]), int(start_date_value[0])
    )
    edate = date(int(end_date_value[2]), int(end_date_value[1]), int(end_date_value[0]))
    delta = edate - sdate
    result = []
    for i in range(delta.days + 1):
        day = sdate + timedelta(days=i)
        result.append(day.strftime("%d-%m-%Y"))
    return result


def get_coin_price(coin_id: str, date: str):
    params = {"id": coin_id, "date": date}
    api_endpoint = Config.API_COIN + f"/coins/{coin_id}/history"
    response = requests.get(api_endpoint, params=params)
    return response.json()


def check_unique_currency_constrain(date: str, coin_id: int, currency_id: int):
    """Kiểm tra xem record có thỏa mãn ràng buộc unique của CryptoPrice"""
    record = (
        db.session.query(CryptoPrice)
        .filter(
            and_(
                CryptoPrice.coin_id == coin_id,
                CryptoPrice.currency_id == currency_id,
                CryptoPrice.date == date,
            )
        )
        .first()
    )

    return True if not record else False


def sync_cryptos_price_history(
    coins_list=None, start_date=None, end_date=None, currency="usd"
):
    """Đồng bộ dữ liệu giá của crypto theo khoảng thời gian
    :param list coins_list: Danh sách các string coin_id của crypto
    :param str start_date: Ngày bắt đầu dd-mm-yyyy
    :param str end_date: Ngày kết thúc dd-mm-yyyy
    :param str currency: Đơn vị quy đổi, mặc định là usd
    """
    dates = get_dates_between(start_date=start_date, end_date=end_date)
    currency_record = (
        db.session.query(Currency).filter(Currency.currency_name == currency).first()
    )
    if not currency_record:
        print(f"Đơn vị tính {currency} không tồn tại, đang tạo mới trên hệ thống")
        new_currency = Currency()
        new_currency.currency_name = currency
        db.session.add(new_currency)
        db.session.commit()
        currency_id = new_currency.id
    else:
        currency_id = currency_record.id

    if isinstance(coins_list, str):
        coins_list = coins_list.split(",")
    for coin_id in coins_list:
        coin_record = (
            db.session.query(CryptoCurrency)
            .filter(CryptoCurrency.gecko_coin_id == coin_id)
            .first()
        )
        if not coin_record:
            raise Exception(f"Crypto với id {coin_id} chưa được hỗ trợ")
        coin_info = to_dict(coin_record)
        for date in dates:
            is_valid_price = check_unique_currency_constrain(
                date=date, coin_id=coin_info.get("id"), currency_id=currency_id
            )
            if not is_valid_price:
                continue
            coin_price_info = get_coin_price(coin_id=coin_id, date=date)
            price = coin_price_info["market_data"]["current_price"].get(currency)
            if not price:
                raise Exception(
                    f"Đơn vị quy đổi {currency} không được hỗ trợ bởi Coin Gecko"
                )
            price_record = CryptoPrice()

            price_record.timestamp = convert_datestring_to_timestamp(date=date)
            price_record.coin_id = coin_info.get("id")
            price_record.currency_id = currency_id
            price_record.price = price
            price_record.date = date
            db.session.add(price_record)
            print(date, coin_id, price)
            # Delay 1s do giới hạn free api coin gecko
            time.sleep(1)
    db.session.commit()
