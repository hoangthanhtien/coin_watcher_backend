# Register Bluereturns/Views.
from gatco.response import json
from application.config import Config
from application.database import redis_db
import string
import random
import ujson


def auth_func(request=None, **kw):
    access_token = request.headers.get("access_token")
    if not access_token:
        return json(Config.AUTH_ERR, 401)
    user_info = redis_db.get(access_token)
    if user_info:
        return ujson.loads(user_info)
    else:
        return json(Config.AUTH_ERR, 401)


def generate_random_string(length=10, type="letters"):
    """Tạo một chuỗi ngẫu nhiên, kiểm tra không trùng lặp trong redis
    :param int length: Độ dài của chuỗi
    :param str type: Loại chuỗi, gồm có lowercase, uppercase, letters, digits, punctuation
    """
    # returning lowercase
    if type == "lowercase":
        letters = string.ascii_lowercase
        return "".join(random.choice(letters) for i in range(length))
    # returning uppercase
    if type == "uppercase":
        letters = string.ascii_uppercase
        return "".join(random.choice(letters) for i in range(length))
    # returning letters
    if type == "letters":
        letters = string.ascii_letters
        return "".join(random.choice(letters) for i in range(length))
    # returning digits
    if type == "digits":
        letters = string.digits
        return "".join(random.choice(letters) for i in range(length))
    # returning punctuation
    if type == "punctuation":
        letters = string.punctuation
        return "".join(random.choice(letters) for i in range(length))


def init_views(app):
    import application.controllers.user
    import application.controllers.crypto_currency
    import application.controllers.prices
    import application.controllers.notification

    @app.route("/")
    def index(request):
        return json({"hello": "world"})
