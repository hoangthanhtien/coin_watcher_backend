### Ứng dụng tracking giá crypto:

- Hiển thị biểu đồ chênh lệch giá gần nhất ngay trên terminal

```bash
python manage.py show_curr_chart <chuỗi mã crypto, viết liền, ngăn cách bởi dấu phẩy>
#python manage.py show_curr_chart binancecoin,ethereum 
```

<img src="/static/images/show_curr_chart.png"></img>
<img src="/static/images/show_curr_chart_2.png"></img>
- Tự động gửi email cảnh báo khi giá tụt xuống một mức nhất định


**Đăng ký user** : Khi gửi thông báo sẽ gửi qua email đã đăng ký 
```curl
curl --location --request POST 'http://0.0.0.0:8090/user/register' \
--header 'Content-Type: application/json' \
--header 'Cookie: session=e30.YT9LGA.wwBCAVBPco_1EDHSZ_8rcCO-VjI' \
--data-raw '        {
            "email":"hoangthanhtien0604@gmail.com",
            "password":"123456",
            "full_name":"Hoàng Thành Tiến",
            "user_name":"tienvjppro"
        }'
```

**Đăng nhập**
```curl
curl --location --request POST 'http://0.0.0.0:8090/user/login' \
--header 'Content-Type: application/json' \
--data-raw '{
    "email":"hoangthanhtien0604@gmail.com",
    "password":"123456"
}'
```

**Tạo thông báo giá qua email**
```curl
curl --location --request POST 'http://0.0.0.0:8090/api/v1/notification' \
--header 'access_token: ujYiCmbpWraGGEfWSedvdoVbBympvqfpjThMDWbvuXJleWkWQxhPZyQVLrzVBLJW' \
--header 'Content-Type: application/json' \
--header 'Cookie: session=e30.YUCUZw.D52QU85hKaPmRySZaSx4RtuPFaU' \
--data-raw '{
    "notify_price_at":46200,
    "notify_type":"0",
    "price_status":0,
    "coin_id":10257,
    "user_id": 7,
    "currency_id":1
}'
```

### Hướng dẫn cài đặt
- Yêu cầu có python >= 3.7
- Cài đặt database Postgresql [tại đây](https://www.digitalocean.com/community/tutorials/how-to-install-postgresql-on-ubuntu-20-04-quickstart)
- Cài đặt redis [tại đây](https://www.digitalocean.com/community/tutorials/how-to-install-and-secure-redis-on-ubuntu-20-04)
- Tạo môi trường ảo, git clone và cài các package cần thiết:
- Cài đặt [termgraph](https://github.com/mkaz/termgraph.git) nếu có sử dụng để show biểu đồ trên terminal

```bash
python3 -m venv coin_watcher
cd coin_watcher
git clone https://github.com/hoangthanhtien/coin_watcher_backend.git repo
cd repo
source ../bin/activate
pip install -r requirements.txt
```

- Tạo mới database tại postgres:

```bash
sudo su postgres
psql
CREATE DATABASE coin_watcher ENCODING = 'utf-8';
CREATE USER coin_watcher_user WITH PASSWORD '123456';
GRANT ALL PRIVILEGES ON DATABASE coin_watcher to coin_watcher_user;
```

- Migrage model vào database:

```bash
rm -rf alembic/versions
mkdir alembic/versions
alembic revision --autogenerate -m "init"
alembic upgrade head
```
- Setup cronjob để thực hiện đồng bộ giá crypto, sửa file `sync_coin_price.sh` cho đúng đường dẫn đã cài đặt phần mềm. Như ví dụ ở dưới đang cài tại `/home/tienhoang/sourceCode/python/coin_watcher/repo`

```
#! /bin/bash
cd /home/tienhoang/sourceCode/python/coin_watcher/repo
source /home/tienhoang/sourceCode/python/coin_watcher/bin/activate
/home/tienhoang/sourceCode/python/coin_watcher/bin/python3 manage.py sync_recent_coin_prices
```

- Vào phần cài đặt crontab
```bash
crontab -e
```
- Paste đoạn sau vào file để thực hiện đồng bộ giá 5 phút một lần, sửa cho đúng đường dẫn
```
*/5 * * * * /home/tienhoang/sourceCode/python/coin_watcher/repo/sync_coin_price.sh
```
