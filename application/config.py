import os
class Config(object):
    DEBUG = True
    STATIC_URL = "static"
    SQLALCHEMY_DATABASE_URI = (
        f"postgresql://{os.environ['POSTGRES_USER']}:{os.environ['POSTGRES_PASSWORD']}@database:{os.environ['POSTGRES_DOCKER_PORT']}/{os.environ['POSTGRES_DB']}"
    )
    AUTH_LOGIN_ENDPOINT = "login"
    AUTH_PASSWORD_HASH = "sha512_crypt"
    AUTH_PASSWORD_SALT = "ruewhndjsa17heaw"
    SECRET_KEY = "e2q8dhaushdauwd7qye"
    SESSION_COOKIE_SALT = "dhuasud819wubadhysagd"
    API_COIN = "https://api.coingecko.com/api/v3"
    REDIS_HOST = "cache"
    REDIS_PORT = "6379"
    REDIS_DB = 0

    BAD_REQUEST_ERR = {"error": "Request Body không hợp lệ"}
    METHOD_NOT_ALLOW_ERR = {"error": "Request Method không hợp lệ"}
    DUPLICATE_EMAIL_ERR = {"error": "Email này đã tồn tại với tài khoản khác"}
    SERVER_ERROR = {"error": "Có lỗi xảy ra, vui lòng thử lại sau"}
    SEND_EMAIL_ERR = {"error": "Gửi email thất bại"}
    LOGIN_ERR = {
        "error": "LOGIN_FAILED",
        "error_message": "user does not exist or incorrect password",
    }
    AUTH_ERR = {"error": "Access Token không hợp lệ"}

    SENDER_ACCOUNT = ""
    SENDER_ACCOUNT_PASSWORD = ""

    WELCOME_MAIL_TEMPLATE = "email_templates/welcome.txt"
    WELCOME_MAIL_HEADER = "Welcome To Coinwatcher!"
    VALIDATE_MAIL_TEMPLATE = "email_templates/send_validate_code.txt"
    VALIDATE_MAIL_HEADER = "This is your validecode on Coinwatcher"
    NOTIFY_PRICE_MAIL_HEADER = "COIN WATCHER!!!!!!!"
    NOTIFY_PRICE_MAIL_TEMPLATE = "email_templates/notify_price.txt"

    CHAT_BOT_WEBHOOKS = "https://stupidchatbot.herokuapp.com/send_noti"
    CHAT_BOT_VERIFY_TOKEN = ""
    WEBSOCKET_MAX_SIZE = 2 ** 20
    WEBSOCKET_MAX_QUEUE = 32
    WEBSOCKET_READ_LIMIT = 2 ** 16
    WEBSOCKET_WRITE_LIMIT = 2 ** 16
