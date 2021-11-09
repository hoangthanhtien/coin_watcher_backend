""" Module for managing tasks through a simple cli interface. """
# Libraries

from websockets import protocol
from application.workers.sync_cryptos_price_history import sync_cryptos_price_history
import sys
from os.path import abspath, dirname

sys.path.insert(0, dirname(abspath(__file__)))
import random
import string
import sqlalchemy
import json
from application.workers.sycn_coin_list import sync_coin_list
from application.workers.sync_recent_price import sync_recent_price
from application.workers.show_curr_price_chart import show_curr_price_chart

from manager import Manager

from application import run_app
from application.database import db

from application.extensions import auth
from application.models.model import User
from datetime import datetime

# Constants.
manager = Manager()


@manager.command
def run():
    """Starts server on port 8000."""
    run_app(host="0.0.0.0", port=8090)


@manager.command
def sync_list_coin():
    """Đồng bộ danh sách coin"""
    sync_coin_list()


@manager.command
def show_curr_chart(coin_list):
    """Hiển thị biểu đồ giá hiện tại"""
    show_curr_price_chart(coin_list)


@manager.command
def sync_recent_coin_prices():
    """Đồng bộ giá hiện tại của coin, cache trên redis"""
    sync_recent_price()


@manager.command
def sync_coin_price():
    """Đồng bộ danh sách coin"""
    today = str(datetime.today().strftime('%d-%m-%Y'))
    print("today",today)
    sync_cryptos_price_history(
        coins_list="bitcoin,ethereum,ripple,binancecoin",
        start_date="01-9-2021",
        end_date=today,
    )


@manager.command
def update_admin(password="123456"):
    user = User.query.filter(User.user_name == "admin").first()
    if user is not None:

        # create user password
        user_password = auth.encrypt_password(password, user.salt)
        user.password = user_password
        db.session.commit()  # type: ignore


@manager.command
def create_admin(password="123456"):
    """Create default data."""


#     role_admin = Role.query.filter(Role.role_name == "admin").first()
#     if(role_admin is None):
#         role_admin = Role(role_name='admin', display_name="Admin")
#         db.session.add(role_admin)# type: ignore
#         db.session.flush()# type: ignore
#
#     role_user = Role.query.filter(Role.role_name == "user").first()
#     if(role_user is None):
#         role_user = Role(role_name='user', display_name="User")
#         db.session.add(role_user)# type: ignore
#         db.session.flush()# type: ignore
#
#
#     user = User.query.filter(User.user_name == "admin").first()
#     if user is None:
#         # create salt
#         letters = string.ascii_lowercase
#         user_salt = ''.join(random.choice(letters) for i in range(64))
#         print("user_salt", user_salt)
#         # create user password
#         user_password=auth.encrypt_password(password, user_salt)
#
#         #create user
#         user = User(user_name='admin', full_name="Admin User", email="admin@gonrin.com",\
#             password=user_password, salt=user_salt)
#
#         db.session.add(user)# type: ignore
#
#     db.session.commit()# type: ignore
#
#     return

if __name__ == "__main__":
    manager.main()
