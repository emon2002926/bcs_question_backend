from django.db import models

from django.contrib.auth.models import AbstractUser
from datetime import timedelta
from django.utils import timezone
import random 

class User(AbstractUser):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, blank=True)
    is_verified = models.BooleanField(default=False)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []


class OTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)    
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def generate_code(self):
        self.code = str(random.randint(100000, 999999))
        self.save()

    def can_resend(self):
        # Allow resend after 60 seconds
        return timezone.now() > self.created_at + timedelta(seconds=60)

    def is_expired(self):
        # OTP expires after 5 minutes
        return timezone.now() > self.created_at + timedelta(minutes=5)


class PasswordResetOTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def generate_code(self):
        self.code = str(random.randint(100000, 999999))
        self.save()

    def is_expired(self):
        return timezone.now() > self.created_at + timedelta(minutes=5)

    def can_resend(self):
        # Allow resend after 60 seconds
        return timezone.now() > self.created_at + timedelta(seconds=60)