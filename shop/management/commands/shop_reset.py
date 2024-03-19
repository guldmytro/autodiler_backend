import os
from django.core.management import call_command
from django.core.management import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Delete existing db.sqlite3, reset migrations, create a superuser'

    def handle(self, *args, **options):
        # Deleting all migrations files
        migration_dir = 'shop/migrations/'
        for filename in os.listdir(migration_dir):
            file_path = os.path.join(migration_dir, filename)
            if os.path.isfile(file_path) and filename != '__init__.py':
                os.remove(file_path)

        # Deleting database sqlite3
        db_file = 'db.sqlite3'
        if os.path.exists(db_file):
            os.remove(db_file)

        # Run migrations
        call_command('makemigrations', 'shop')
        call_command('migrate')

        # Creating superuser admin with admin password
        call_command('createsuperuser', interactive=False,
                     username='admin', email='')
        admin = User.objects.get(username='admin')
        admin.set_password('admin')
        admin.save()
