from application.models.model import CryptoCurrency
from application.extensions import apimanager
from application.controllers import auth_func

apimanager.create_api(collection_name='crypto_currency', model=CryptoCurrency,
    methods=['GET', 'POST', 'DELETE', 'PUT'],
    url_prefix='/api/v1',
    preprocess=dict(GET_SINGLE=[auth_func], GET_MANY=[auth_func], POST=[auth_func], PUT_SINGLE=[auth_func]),
    )
