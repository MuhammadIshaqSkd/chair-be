import uuid

from django.db import models
from datetime import timedelta
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
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
        ('Freelancer', 'Freelancer'),
        ('Owner', 'Owner'),
    )
    email = models.EmailField(_("Email"), unique=True)
    profession = models.CharField(_("Profession"), max_length=255, null=True, blank=True)
    normalized_email = models.EmailField(_("Normalized Email"), unique=True, blank=True)
    password = models.CharField(_("Mot de passe"), max_length=256)
    username = models.CharField(_("Nom d'utilisateur"), max_length=150, null=True, blank=True)
    full_name = models.CharField(_("Nom et prénom"), max_length=255, null=True, blank=True)
    phone_number = models.CharField(_("Numéro de contact"), max_length=50, blank=True, null=True)
    token = models.CharField(_("Token"), max_length=300, null=True, blank=True)
    token_expiry = models.DateTimeField(_("Token Expiry"), default=timezone.now)
    sign_up_with = models.CharField(_("Inscrivez-vous avec"), max_length=60, default="email")
    profile_photo = models.ImageField(
        _("Photo de profil"),
        upload_to=upload_to_uuid('profile_photos/'),
        null=True,
        blank=True
    )
    account_type = models.CharField(
        _("Type de compte"),
        max_length=60,
        default="Freelancer",
        choices=TYPE_CHOICES
    )

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

    def clean(self):
        """
        Perform custom validations here.
        """
        # Ensure the normalized_email is unique
        if self.email:
            normalized_email = self.get_normalized_email(self.email)
            if User.objects.exclude(pk=self.pk).filter(normalized_email=normalized_email).exists():
                raise ValidationError(_("A user with this email already exists."))

        # Validate business profile for "Owner" account type
        if self.account_type.lower() == "owner":
            if not UserBusinessProfile.objects.filter(user=self).exists():
                raise ValidationError(_("User Business Profile does not exist for an Owner account."))

        # Ensure username is unique
        if not self.username:
            base_username = self.email.split('@')[0]
            new_username = base_username
            counter = 1
            while User.objects.filter(username=new_username).exclude(pk=self.pk).exists():
                new_username = f"{base_username}{counter}"
                counter += 1
            self.username = new_username

    def save(self, *args, **kwargs):
        # Normalize email
        if self.email:
            self.normalized_email = self.get_normalized_email(self.email)

        # Generate token if it's a new instance or token is None
        if not self.pk or not self.token:
            self.token = uuid.uuid4().hex[:20]
            self.token_expiry = timezone.now() + timedelta(minutes=30)

        # Validate the object
        self.clean()

        super().save(*args, **kwargs)

    def delete(self, using=None, keep_parents=False):
        """
        Delete related profile-photo from storage.
        """
        try:
            if self.profile_photo and self.profile_photo.name:
                self.profile_photo.storage.delete(self.profile_photo.name)
        except Exception as e:
            print(f"Error deleting profile photo: {e}")
        super().delete(using, keep_parents)

    def __str__(self):
        return self.email

class UserBusinessProfile(TimeStampedModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    business_name = models.CharField(_("Nom de l'entreprise"), max_length=255)
    location = models.CharField(_("emplacement"), max_length=255)
    workspace = models.CharField(_("Espace de travail"), max_length=255)
    business_logo = models.ImageField(_("Logo d'entreprise"), upload_to=upload_to_uuid('business_logos/'), null=True, blank=True)
    business_website = models.URLField(_("Site Web"), max_length=255, null=True, blank=True)
    description = models.TextField(_("Description ou détails"))
    business_email = models.EmailField(_("E-mail de contact"), max_length=255, null=True, blank=True)
    phone_number = models.CharField(_("Numéro de contact"), max_length=150)
    total_reviews = models.IntegerField(_("Total des avis"), default=0)
    total_ratings = models.FloatField(_("Note totale"), default=0.0)
    rating = models.FloatField(_("notation"), default=0.0)

    class Meta:
        verbose_name = _("Profil du propriétaire")
        verbose_name_plural = _("Profils de propriétaires")

    def save(self, *args, **kwargs):
        self.rating = round((self.total_ratings / self.total_reviews), 2) if self.total_reviews > 0 else 0.0
        super().save(**kwargs)


    def delete(self, using=None, keep_parents=False):
        # Delete related business_logo from storage
        try:
            if self.business_logo.name:
                self.business_logo.storage.delete(self.business_logo.name)
        except Exception as e:
            print(e)
        super().delete(using, keep_parents)

    def __str__(self):
        return f'{self.business_name} - {self.user.email}'
