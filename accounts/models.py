# accounts/models.py

from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        MANAGER = "MANAGER", "Manager"
        TEAM_MEMBER = "TEAM_MEMBER", "Team Member"

    role = models.CharField(max_length=50, choices=Role.choices, default=Role.ADMIN)