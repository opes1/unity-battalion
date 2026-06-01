release: python manage.py collectstatic --noinput --clear && python manage.py migrate
web: gunicorn unity_battalion.wsgi --log-file -
