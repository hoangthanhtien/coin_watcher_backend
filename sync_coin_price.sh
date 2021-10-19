#! /bin/bash
cd /home/vmo/sourceCode/python/coin_watcher
source /home/vmo/sourceCode/python/coin_watcher/venv/bin/activate
/home/vmo/sourceCode/python/coin_watcher/venv/bin/python3 manage.py sync_recent_coin_prices
