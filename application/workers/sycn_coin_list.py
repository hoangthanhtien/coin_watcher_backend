from application import app
from application.database import db
from application.models.model import CryptoCurrency, CryptoPlatform
import requests

def sync_coin_list():
    '''Đồng bộ danh sách coin từ gecko
    '''
    api_url = app.config.get("API_COIN")+'/coins/list?include_patform=true'
    response = requests.get(api_url)
    #print(response.json())
    count = 0
    for coin in response.json():
        coin_id = coin.get("id")
        coin_symbol = coin.get("symbol")
        coin_name = coin.get("name")
        coin_platform = coin.get("platforms")
        platform_name = None
        platform_id = None
        #### Sync platform

        if coin_platform:
            platform_name = list(coin_platform.keys())[0]
            print("platform_name", platform_name)

        if coin_platform and coin_platform != {}:
            platform_existed = db.session.query(CryptoPlatform)\
                    .filter(CryptoPlatform.platform_name == platform_name)\
                    .first()
            if not platform_existed:
                new_crypto_platform = CryptoPlatform()
                new_crypto_platform.platform_name = platform_name
                platform_id = new_crypto_platform.id
                db.session.add(new_crypto_platform)
                db.session.commit()

        #### Sync Coin 
        coin_existed = db.session.query(CryptoCurrency)\
                .filter(CryptoCurrency.gecko_coin_id == coin_id)\
                .first()
        if coin_existed:
            pass
        else:
            new_coin = CryptoCurrency()
            new_coin.coin_name = coin_name
            new_coin.gecko_coin_id = coin_id 
            new_coin.symbol = coin_symbol 
            new_coin.platform_id = platform_id if platform_id else None
            print("new_coin",new_coin)
            db.session.add(new_coin)
            db.session.commit()
            print(f"Đã add coin {coin_name} với nền tảng {platform_name}")
            count += 1
    print(f"Đã add {count} coins") 
