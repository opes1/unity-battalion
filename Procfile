release: python manage.py create_superuser_auto && python manage.py migrate
web: gunicorn unity_battalion.wsgi --log-file - --workers 2
