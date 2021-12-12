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
