#!/bin/bash
source .env
if [[ -z "${POSTGRES_LOCAL_PORT}" ||  -z "${POSTGRES_USER}" ||  -z "${POSTGRES_PASSWORD}"|| -z "${POSTGRES_DB}" ]]; then
  echo "Missing environment variables, please set the env in .env file"
  exit 1
else
  echo "POSTGRES_LOCAL_PORT" ${POSTGRES_LOCAL_PORT}
  echo "POSTGRES_USER" ${POSTGRES_USER}
  echo "POSTGRES_PASSWORD" ${POSTGRES_PASSWORD}
  echo "POSTGRES_DB" ${POSTGRES_DB}
fi

export PGPASSWORD=${POSTGRES_PASSWORD}
psql --username ${POSTGRES_USER} -w --dbname ${POSTGRES_DB} -h localhost -p ${POSTGRES_LOCAL_PORT} -c "drop table alembic_version" 

MIGRATE_VERSIONS=./alembic/versions/
if test -d "$MIGRATE_VERSIONS"; then
  echo "Migration version folder exists, deleting..."
  rm -rf ./alembic/versions/
  echo "Deleted!"
  echo "Recreating version folder for migration"
  mkdir alembic/versions
  echo "Created!"
else
  echo "Migration version folder not exists, creating..."
  mkdir alembic/versions
  echo "Created!"
fi

./venv/bin/alembic revision --autogenerate -m "Migrate models" 
./venv/bin/alembic upgrade head 
