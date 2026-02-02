from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from faker import Faker
from accounts.models import Student

User = get_user_model()
fake = Faker("ar_SA")   # Saudi Arabic

class Command(BaseCommand):
    help = "Seed database with fake students"

    def handle(self, *args, **kwargs):

        for i in range(20):

            # 1) Create Django User (for login)
            user = User.objects.create_user(
                username=fake.user_name(),
                email=fake.email(),
                password="Test12345"   # same password for all fake users
            )

            # 2) Create Student profile linked to that user
            Student.objects.create(
                user=user,
                full_name=fake.name(),
                major=fake.job()
            )

        self.stdout.write(
            self.style.SUCCESS("Fake students inserted successfully!")
        )
