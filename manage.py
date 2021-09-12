""" Module for managing tasks through a simple cli interface. """
# Libraries

from application.workers.sync_cryptos_price_history import sync_cryptos_price_history
import sys
from os.path import abspath, dirname

sys.path.insert(0, dirname(abspath(__file__)))
import random
import string
import sqlalchemy
import json
from application.workers.sycn_coin_list import sync_coin_list

from manager import Manager

from application import run_app
from application.database import db

from application.extensions import auth
from application.models.model import User

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
def sync_coin_price():
    """Đồng bộ danh sách coin"""
    sync_cryptos_price_history(
        coins_list="bitcoin,ethereum", start_date="10-08-2021", end_date="10-09-2021"
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
