from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import UserProfile

class Command(BaseCommand):
    help = 'Setup initial data for the application'

    def handle(self, *args, **options):
        # Create admin user
        if not User.objects.filter(username='admin').exists():
            admin_user = User.objects.create_user(
                username='admin',
                password='admin123',
                is_staff=True,
                is_superuser=True
            )
            UserProfile.objects.create(
                user=admin_user,
                mobile='9999999999',
                role='admin'
            )
            self.stdout.write(self.style.SUCCESS('Admin user created: admin/admin123'))

        # Create delivery partners
        for i in range(1, 4):
            mobile = f'987654321{i}'
            username = f'delivery_{i}'
            
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(
                    username=username,
                    password='delivery123'
                )
                UserProfile.objects.create(
                    user=user,
                    mobile=mobile,
                    role='delivery_partner'
                )
                self.stdout.write(self.style.SUCCESS(f'Delivery partner created: {username} (Mobile: {mobile})'))

        self.stdout.write(self.style.SUCCESS('Initial data setup completed!'))