import yaml
from django.core.management.base import BaseCommand, CommandError
from polls.models import User

class Command(BaseCommand):
    help = 'Imports users from a YAML file.'

    def add_arguments(self, parser):
        parser.add_argument('yaml_file', type=str, help='The path to the YAML file to import.')

    def handle(self, *args, **options):
        yaml_file_path = options['yaml_file']

        try:
            with open(yaml_file_path, 'r') as file:
                users_data = yaml.safe_load(file)
        except FileNotFoundError:
            raise CommandError(f'File "{yaml_file_path}" does not exist.')
        except yaml.YAMLError as e:
            raise CommandError(f'Error parsing YAML file: {e}')

        if not isinstance(users_data, list):
            raise CommandError('The YAML file must contain a list of users.')

        for user_data in users_data:
            username = user_data.get('username')
            password = user_data.get('password')
            role = user_data.get('role', 'student')
            student_id = user_data.get('student_id')
            department = user_data.get('department')
            year = user_data.get('year')
            first_name = user_data.get('first_name', '')
            last_name = user_data.get('last_name', '')

            if not username or not password:
                self.stdout.write(self.style.WARNING(f'Skipping user with missing username or password.'))
                continue

            if User.objects.filter(username=username).exists():
                self.stdout.write(self.style.WARNING(f'User "{username}" already exists. Skipping.'))
                continue

            try:
                user = User.objects.create_user(
                    username=username,
                    password=password,
                    role=role,
                    student_id=student_id,
                    department=department,
                    year=year,
                    first_name=first_name,
                    last_name=last_name
                )
                self.stdout.write(self.style.SUCCESS(f'Successfully created user "{user.username}"'))
            except Exception as e:
                raise CommandError(f'Error creating user "{username}": {e}')
