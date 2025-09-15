from django.core.management.base import BaseCommand
from polls.models import User, Election, Position, Candidate
from datetime import datetime, timedelta

class Command(BaseCommand):
    help = 'Populates the database with sample data'

    def handle(self, *args, **options):
        self.stdout.write('Deleting existing data...')
        User.objects.filter(is_superuser=False).delete()
        Election.objects.all().delete()
        Position.objects.all().delete()
        Candidate.objects.all().delete()

        self.stdout.write('Creating new data...')

        # Create users
        users = []
        for i in range(1, 11):
            user = User.objects.create_user(
                username=f'student{i}',
                password='password',
                first_name=f'Student',
                last_name=f'{i}',
                student_id=f'STU{i:03}',
                department='Computer Science',
                year=2023
            )
            users.append(user)

        User.objects.create_user(username='Archit', password='password')

        # Create election
        election = Election.objects.create(
            name='College Union Election 2025',
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(days=7)
        )

        # Create positions
        president_position = Position.objects.create(name='President', election=election)
        vp_position = Position.objects.create(name='Vice President', election=election)

        # Create candidates
        Candidate.objects.create(user=users[0], position=president_position, bio='I will bring change!')
        Candidate.objects.create(user=users[1], position=president_position, bio='I am the best for this role.')

        Candidate.objects.create(user=users[2], position=vp_position, bio='Vote for me!')
        Candidate.objects.create(user=users[3], position=vp_position, bio='I will work for you.')

        self.stdout.write(self.style.SUCCESS('Successfully populated the database.'))
