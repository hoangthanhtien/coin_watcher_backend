from gatco_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
import redis
from application.config import Config

redis_db = redis.Redis(
    host=Config.REDIS_HOST, port=Config.REDIS_PORT, db=Config.REDIS_DB
)


def init_database(app):
    db.init_app(app)
