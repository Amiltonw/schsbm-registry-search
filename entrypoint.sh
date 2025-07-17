#!/bin/sh
set -e

export PGPASSWORD=postgres

until psql -h db -U postgres -d nrn_search -c '\q'; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done

>&2 echo "Postgres is up - executing command"

python manage.py migrate --noinput

exec "$@"
