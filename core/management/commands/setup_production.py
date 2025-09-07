from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.core.management import call_command


class Command(BaseCommand):
    help = 'Setup production database with migrations and superuser'

    def handle(self, *args, **options):
        self.stdout.write('🚀 Setting up production database...')
        
        # Make migrations
        self.stdout.write('📝 Creating migrations...')
        call_command('makemigrations', verbosity=1)
        
        # Apply migrations
        self.stdout.write('🔄 Applying migrations...')
        call_command('migrate', verbosity=1)
        
        # Create superuser
        self.stdout.write('👤 Creating superuser...')
        User = get_user_model()
        if not User.objects.filter(is_superuser=True).exists():
            User.objects.create_superuser(
                username='admin',
                email='initcore25@gmail.com',
                password='0987poiu'
            )
            self.stdout.write(
                self.style.SUCCESS('✅ Superuser created (username=admin, password=0987poiu)')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS('✅ Superuser already exists')
            )
        
        self.stdout.write(
            self.style.SUCCESS('🎉 Production setup completed successfully!')
        )
