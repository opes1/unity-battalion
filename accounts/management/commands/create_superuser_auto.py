from django.core.management.base import BaseCommand
from accounts.models import User
from decouple import config


class Command(BaseCommand):
    help = 'Create superuser automatically from environment variables'

    def handle(self, *args, **kwargs):
        username = config('DJANGO_SUPERUSER_USERNAME', default='admin')
        email = config('DJANGO_SUPERUSER_EMAIL', default='admin@unitybattalion.org')
        password = config('DJANGO_SUPERUSER_PASSWORD', default='Admin@BB2024!')

        if not User.objects.filter(username=username).exists():
            u = User.objects.create_superuser(
                username=username,
                email=email,
                password=password,
            )
            u.role = 'super_admin'
            u.is_approved = True
            u.is_active = True
            u.save()
            self.stdout.write(f'Superuser {username} created successfully')
        else:
            self.stdout.write(f'Superuser {username} already exists - skipping')
