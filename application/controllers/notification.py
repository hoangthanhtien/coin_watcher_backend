from application.models.model import Notification
from application.extensions import apimanager
from application.controllers import auth_func

apimanager.create_api(
    collection_name="notification",
    model=Notification,
    methods=["GET", "POST", "DELETE", "PUT"],
    url_prefix="/api/v1",
    preprocess=dict(
        GET_SINGLE=[auth_func],
        GET_MANY=[auth_func],
        POST=[],
        PUT_SINGLE=[auth_func],
    ),
)
