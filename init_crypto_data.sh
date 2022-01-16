#! /bin/bash
./venv/bin/python3 manage.py sync_list_coin

export PGPASSWORD=${POSTGRES_PASSWORD}
psql --username ${POSTGRES_USER} -w --dbname ${POSTGRES_DB} -h localhost -p ${POSTGRES_LOCAL_PORT} -c "update crypto_currency set is_follow=true where gecko_coin_id in('bitcoin','cardano','binancecoin','ripple')" 
echo "Set default followd coin : BTC, ADA, BNB, XRP"
