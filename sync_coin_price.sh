#! /bin/bash
cd /home/tinehoang/sourceCode/python/coin_watcher_backend
source /home/tinehoang/sourceCode/python/coin_watcher_backend/venv/bin/activate 
/home/tinehoang/sourceCode/python/coin_watcher_backend/venv/bin/python3.7 manage.py sync_recent_coin_prices
