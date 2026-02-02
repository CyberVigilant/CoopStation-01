from django.conf import settings
from django.db import models

class Student(models.Model):
    user = models.OneToOneField(
    settings.AUTH_USER_MODEL,
    on_delete=models.CASCADE,
    related_name="student_profile"
    )
    full_name = models.CharField(max_length=150, blank=True)
    major = models.CharField(max_length=120, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username
