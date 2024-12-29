import uuid

from django.db import models
from datetime import timedelta
from django.utils import timezone
from django_uuid_upload import upload_to_uuid

from django.contrib.auth.models import (
    AbstractUser,
    BaseUserManager,
)


class UserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError("The given email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("username", email)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=256, null=True, blank=True)
    username = models.CharField(max_length=60, null=True, blank=True)
    full_name = models.CharField(max_length=60, null=True, blank=True)
    phone_number = models.CharField(max_length=30, null=True, blank=True)
    token = models.CharField(max_length=300, null=True, blank=True)
    token_expiry = models.DateTimeField(default=timezone.now)
    sign_up_with = models.CharField(max_length=60, default="email")
    profile_photo = models.ImageField(upload_to=upload_to_uuid('profile_photos/'), null=True, blank=True)
    USERNAME_FIELD = "email"
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = UserManager()

    def save(self, *args, **kwargs):
        if not self.username:
            base_username = self.email.split('@')[0]
            new_username = base_username
            counter = 1
            # Check if the username exists and increment until unique
            while User.objects.filter(username=new_username).exists():
                new_username = f"{base_username}{counter}"
                counter += 1
            self.username = new_username

        # Generate token if it's a new instance or token is None
        if not self.pk or self.token is None:
            self.token = uuid.uuid4().hex[:20]
            self.token_expiry = timezone.now() + timedelta(minutes=30)
        super().save(*args, **kwargs)


    def delete(self, using=None, keep_parents=False):
        # Delete related profile-image from storage
        try:
            if self.profile_photo.name:
                self.profile_photo.storage.delete(self.profile_photo.name)
        except Exception as e:
            print(e)
        super().delete(using, keep_parents)
