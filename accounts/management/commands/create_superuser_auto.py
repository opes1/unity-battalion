from django.core.management.base import BaseCommand
from accounts.models import User
from decouple import config


class Command(BaseCommand):
    help = 'Create superuser automatically from environment variables'

    def add_arguments(self, parser):
        parser.add_argument(
            '--sync-password',
            action='store_true',
            help='Force-reset the password of an existing superuser to match '
                 'DJANGO_SUPERUSER_PASSWORD. Run manually when needed — never '
                 'part of the automated build command.',
        )

    def handle(self, *args, **options):
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
        elif options['sync_password']:
            u = User.objects.get(username=username)
            u.role = 'super_admin'
            u.is_approved = True
            u.is_active = True
            u.set_password(password)
            u.save()
            self.stdout.write(f'Superuser {username} password synced')
        else:
            self.stdout.write(f'Superuser {username} already exists - skipping')
