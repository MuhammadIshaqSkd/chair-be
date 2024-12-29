import uuid

from django.db import models
from datetime import timedelta
from django.utils import timezone
from django_extensions.db.models import TimeStampedModel
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

    TYPE_CHOICES = (
        ('user', 'user'),
        ('property_owner', 'property_owner'),
    )
    email = models.EmailField(unique=True)
    normalized_email = models.CharField(max_length=255, unique=True, blank=True, null=True)
    password = models.CharField(max_length=256)
    username = models.CharField(max_length=60, null=True, blank=True)
    full_name = models.CharField(max_length=60, null=True)
    phone_number = models.CharField(max_length=30, null=True, blank=True)
    token = models.CharField(max_length=300, null=True, blank=True)
    token_expiry = models.DateTimeField(default=timezone.now)
    sign_up_with = models.CharField(max_length=60, default="email")
    profile_photo = models.ImageField(upload_to=upload_to_uuid('profile_photos/'), null=True, blank=True)
    account_type = models.CharField(max_length=60, default="user", choices=TYPE_CHOICES)

    USERNAME_FIELD = "email"
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = UserManager()

    @staticmethod
    def get_normalized_email(email):
        if not email:
            return ''
        local_part, domain_part = email.lower().split('@')
        return f"{local_part.replace('.', '')}@{domain_part}"


    def save(self, *args, **kwargs):
        # Set normalized_email based on the current email
        if self.email and self.normalized_email is None:
            self.normalized_email = self.get_normalized_email(self.email)

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
        if self.account_type == "property_owner":
            if not UserBusinessProfile.objects.filter(user=self).exists():
                raise Exception("User Business Profile does not exist")
        super().save(*args, **kwargs)

    def delete(self, using=None, keep_parents=False):
        # Delete related profile-image from storage
        try:
            if self.profile_photo.name:
                self.profile_photo.storage.delete(self.profile_photo.name)
        except Exception as e:
            print(e)
        super().delete(using, keep_parents)


class UserBusinessProfile(TimeStampedModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    business_name = models.CharField(max_length=255)
    business_description = models.TextField()
    business_logo = models.ImageField(upload_to=upload_to_uuid('business_logos/'), null=True, blank=True)

    class Meta:
        verbose_name_plural = "User Business Profiles"
        verbose_name = "User Business Profile"

    def delete(self, using=None, keep_parents=False):
        # Delete related business_logo from storage
        try:
            if self.business_logo.name:
                self.business_logo.storage.delete(self.business_logo.name)
        except Exception as e:
            print(e)
        super().delete(using, keep_parents)
