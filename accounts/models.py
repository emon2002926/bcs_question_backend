from django.db import models

from django.contrib.auth.models import AbstractUser, BaseUserManager
from datetime import timedelta
from django.utils import timezone
import random 

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

class User(AbstractUser):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, blank=True)
    is_verified = models.BooleanField(default=False)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    objects = CustomUserManager()


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