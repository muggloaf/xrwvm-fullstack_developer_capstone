#!/bin/sh
set -eu
# Make migrations and migrate the database.
echo "Making migrations and migrating the database. "
python manage.py migrate --noinput
python manage.py collectstatic --noinput
exec "$@"
