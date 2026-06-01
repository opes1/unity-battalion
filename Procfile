release: python manage.py collectstatic --noinput && python manage.py migrate
web: gunicorn unity_battalion.wsgi --log-file -
