# accounts/models.py

from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    class Role(models.TextChoices):
        MANAGEMENT = "MANAGEMENT", "Management"
        MANAGER = "MANAGER", "Manager"

    role = models.CharField(max_length=50, choices=Role.choices, default=Role.MANAGER)
    
    # Add these new fields
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    department = models.CharField(max_length=100, blank=True, null=True)