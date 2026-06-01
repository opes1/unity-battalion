from django.core.management.base import BaseCommand
from accounts.models import User


class Command(BaseCommand):
    help = 'Create superuser automatically from environment variables'

    def handle(self, *args, **kwargs):
        if not User.objects.filter(username='admin').exists():
            u = User.objects.create_superuser(
                username='admin',
                email='opeoyinlola11@gmail.com',
                password='Admin@Railway2024',
            )
            u.role = 'super_admin'
            u.is_approved = True
            u.is_active = True
            u.save()
            self.stdout.write('Superuser created successfully')
        else:
            u = User.objects.get(username='admin')
            u.role = 'super_admin'
            u.is_approved = True
            u.is_active = True
            u.set_password('Admin@Railway2024')
            u.save()
            self.stdout.write('Superuser updated successfully')
