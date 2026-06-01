from django.core.management.base import BaseCommand
from accounts.models import User


class Command(BaseCommand):
    help = 'Create superuser automatically from environment variables'

    def handle(self, *args, **kwargs):
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin',
                email='opeoyinlola11@gmail.com',
                password='Admin@Railway2024',
                role='super_admin',
                is_approved=True,
            )
            self.stdout.write('Superuser created successfully')
        else:
            self.stdout.write('Superuser already exists')
