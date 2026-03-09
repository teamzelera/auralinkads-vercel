"""
Accounts app — Admin user authentication (JWT)
"""
from django.db import models
from django.contrib.auth.models import AbstractUser


class AdminUser(AbstractUser):
    """Extended user model for AuraLink admins."""
    class Meta:
        verbose_name = "Admin User"
        verbose_name_plural = "Admin Users"
