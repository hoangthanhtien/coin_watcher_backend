""" Module represents a User. """

from sqlalchemy import (
    Column,
    String,
    Integer,
    Boolean,
    ForeignKey,
    BigInteger,
    DECIMAL,
    SmallInteger,
    FLOAT,
)

from sqlalchemy import Column, String, Integer, Boolean, ForeignKey

from sqlalchemy.orm import relationship

from application.database import db
from application.database.model import CommonModel


class User(CommonModel):
    """Thông tin người dùng
    :atr int id: id khóa chính của user_id
    :atr str user_name: Tên người dùng
    :atr str full_name: Tên đầy đủ
    :atr str email: Thông tin email
    :atr str password: Mật khẩu
    :atr str salt: Dải salt để mã hóa mật khẩu
    :atr str fb_messenger_pid: id liên lạc của người dùng trên Facebook messenger
    :atr bool is_active: Trạng thái active của người dùng, có bị khóa tài khoản hay không
    """

    __tablename__ = "user"

    id = db.Column(Integer, autoincrement=True, primary_key=True)

    # Authentication Attributes.
    user_name = db.Column(String(255), nullable=True, index=True)
    full_name = db.Column(String(255), nullable=True)
    email = db.Column(String(255), nullable=False, index=True, unique=True)
    password = db.Column(String(255), nullable=False)
    salt = db.Column(String(255), nullable=False)
    fb_messenger_pid = db.Column(String(255), nullable=True)

    # Permission Based Attributes.
    is_active = db.Column(Boolean, default=True)

    # Methods
    def __repr__(self):
        """Show user object info."""
        return "<User: {}>".format(self.id)


class CryptoPlatform(CommonModel):
    """Nền tảng crypto, Ethereum,...
    :atr int id: id khóa chính của platform
    :atr str platform_name: Tên của platform
    """

    __tablename__ = "crypto_platform"
    id = db.Column(Integer, autoincrement=True, primary_key=True)
    platform_name = db.Column(String(100), nullable=False)


class CryptoCurrency(CommonModel):
    """Danh sách tiền ảo
    :atr int id: id khóa chính của platform
    :atr str gecko_coin_id: id của crypto coin trên gecko, cái này dùng để query giá
    :atr str symbol: viết tắt của coin
    :atr str coin_name: Tên của coin
    :atr str platform_id: Mã id của platform của coin , khóa ngoại tới bảng crypto_platform
    """

    __tablename__ = "crypto_currency"
    id = db.Column(Integer, autoincrement=True, primary_key=True)
    gecko_coin_id = db.Column(String(100), nullable=False)
    symbol = db.Column(String(100), nullable=False)
    coin_name = db.Column(String(100), nullable=False)
    platform_id = db.Column(Integer, ForeignKey("crypto_platform.id"))
    platform = db.relationship("CryptoPlatform")


class CryptoPrice(CommonModel):
    """Lịch sử giá của crypto
    :atr int timestamp: Thời gian ghi lại giá của crypto
    :atr str date: Là timestamp nhưng dạng date
    :atr int coin_id: Mã id của crypto
    :atr int currency_id: Đơn vị quy đổi
    :atr float price: Giá crypto
    """

    __tablename__ = "crypto_price"
    id = db.Column(Integer, autoincrement=True, primary_key=True)
    timestamp = db.Column(BigInteger(), nullable=True)
    date = db.Column(String(15), nullable=False)
    coin_id = db.Column(Integer, ForeignKey("crypto_currency.id"))
    coin = db.relationship("CryptoCurrency")
    currency_id = db.Column(Integer, ForeignKey("currency.id"))
    currency = db.relationship("Currency")
    price = db.Column(DECIMAL(), nullable=False)


class Currency(CommonModel):
    """Đơn vị quy đổi của crypto"""

    __tablename__ = "currency"
    id = db.Column(Integer, autoincrement=True, primary_key=True)
    currency_name = db.Column(String(100), nullable=False)


class Notification(CommonModel):
    """Lưu cài đặt thông báo của người dùng
    :atr float notify_price_at: Giá thông báo
    :atr int price_status: 0 - nhỏ hơn hoặc bằng, 1 - lớn hơn hoặc bằng
    :atr str notify_type: là một chuỗi ngăn cách nhau bởi dấu phẩy
        0 - Qua email, 1 - Qua Facebook messenger, 2 - Trực tiếp trên web base
    :atr int coin_id: id của coin, khóa ngoại
    :atr int currency_id: id của đơn vị tiền tệ, khóa ngoại
    :atr int user_id: id của user, khóa ngoại
    :atr bool is_notify: Notification này đã được xử lý hay chưa
    """

    __tablename__ = "notification"
    id = db.Column(Integer, autoincrement=True, primary_key=True)
    notify_price_at = db.Column(DECIMAL(), nullable=False)
    notify_type = db.Column(String(10), nullable=False)
    price_status = db.Column(SmallInteger(), nullable=False)
    coin_id = db.Column(Integer, ForeignKey("crypto_currency.id"))
    coin = db.relationship("CryptoCurrency")
    user_id = db.Column(Integer, ForeignKey("user.id"))
    user = db.relationship("User")
    currency_id = db.Column(Integer, ForeignKey("currency.id"))
    currency = db.relationship("Currency")
    is_notify = db.Column(Boolean, default=False)
