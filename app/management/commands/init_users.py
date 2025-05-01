# app/management/commands/init_users.py
from django.core.management.base import BaseCommand
import bcrypt
from app.models import User

class Command(BaseCommand):
    help = 'Initialize test and admin users'

    def handle(self, *args, **options):
        if not User.objects.filter(username='test_user').exists():
            hashed_password = bcrypt.hashpw('password1'.encode(), bcrypt.gensalt()).decode()
            User.objects.create(
                id=User.objects.count() + 1,
                username='test_user',
                hashed_password=hashed_password,
                points=0,
                is_admin=False
            )
            self.stdout.write(self.style.SUCCESS('Created test_user'))
        if not User.objects.filter(username='admin').exists():
            hashed_password = bcrypt.hashpw('1234567890'.encode(), bcrypt.gensalt()).decode()
            User.objects.create(
                id=User.objects.count() + 1,
                username='admin',
                hashed_password=hashed_password,
                points=0,
                is_admin=True
            )
            self.stdout.write(self.style.SUCCESS('Created admin'))

