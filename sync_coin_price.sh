#! /bin/bash
cd /home/tienhoang/sourceCode/python/coin_watcher_backend
source /home/tienhoang/sourceCode/python/coin_watcher_backend/venv/bin/activate
/home/tienhoang/sourceCode/python/coin_watcher_backend/venv/bin/python3 manage.py sync_recent_coin_prices
