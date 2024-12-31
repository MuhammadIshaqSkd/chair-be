from django.core.exceptions import ValidationError
from django.db import models
from django.dispatch import receiver
from django_uuid_upload import upload_to_uuid
from django.db.models.signals import post_delete
from django_extensions.db.models import TimeStampedModel

from auths.models import User, UserBusinessProfile


# Create your models here.
class AdListImage(TimeStampedModel):
    image = models.ImageField(upload_to=upload_to_uuid('ad_listing/images/'))

    class Meta:
        verbose_name_plural = "Ad List Images"
        verbose_name = "Ad List Image"

    def delete(self, using=None, keep_parents=False):
        try:
            if self.image.name:
                self.image.storage.delete(self.image.name)
        except Exception as e:
            print(e)
        super().delete(using, keep_parents)

@receiver(post_delete, sender=AdListImage)
def delete_image_file(sender, instance, **kwargs):
    """
    Deletes the image file from storage when the instance is deleted via bulk delete or other methods.
    """
    try:
        if instance.image.name:
            instance.image.storage.delete(instance.image.name)
    except Exception:
        pass


class AdListing(TimeStampedModel):
    user = models.ForeignKey(UserBusinessProfile, on_delete=models.CASCADE, related_name='owner_user')
    title = models.CharField(max_length=255)
    space_type = models.CharField(max_length=255)
    size = models.CharField(max_length=255)
    availability = models.CharField(max_length=300)
    rental_rate = models.DecimalField(max_digits=10, decimal_places=2)
    ad_images = models.ManyToManyField(AdListImage, related_name="ad_list_images", blank=True)
    location = models.CharField(max_length=300)
    description = models.TextField()
    total_reviews = models.IntegerField(default=0)
    total_ratings = models.FloatField(default=0.0)

    @property
    def rating(self):
        if self.total_reviews > 0:
            return round((self.total_ratings / self.total_reviews), 2)
        return 0.0

    class Meta:
        verbose_name_plural = "Ad Listings"
        verbose_name = "Ad Listing"

    def save(self, *args, **kwargs):
        # Check for existing instance to detect changes
        if self.pk:
            old_instance = AdListing.objects.filter(id=self.id).first()
            old_images = set(old_instance.ad_images.all())
            new_images = set(self.ad_images.all())

            # Find images that are removed
            removed_images = old_images - new_images
            for image in removed_images:
                image.delete()

        # Save the current instance
        super().save(**kwargs)

    def delete(self, *args, **kwargs):
        # Delete related AdListImage instances and their files
        for image in self.ad_images.all():
            image.delete()
        # Call the parent class delete method
        super().delete(*args, **kwargs)

    def __str__(self):
        return self.title

class RentalRequest(TimeStampedModel):
    REQUEST_STATUS = (
        ('pending', 'pending'),
        ('approved', 'approved'),
        ('rejected', 'rejected'),
    )
    ad_list = models.ForeignKey(AdListing, on_delete=models.CASCADE, related_name='ad_listing_rental_requests')
    rental_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rental_user')
    status = models.CharField(max_length=300, default='pending', choices=REQUEST_STATUS)
    is_review = models.BooleanField(default=False)

    class Meta:
            verbose_name_plural = "Rental Requests"
            verbose_name = "Rental Request"

    def save(self, *args, **kwargs):
        # Prevent users from requesting their own ad
        if self.ad_list.user.user == self.rental_user:
            raise ValidationError("You cannot create a rental request for your own ad.")
        super().save(**kwargs)

    def __str__(self):
        return f"{self.rental_user.email} - {self.status}"


class AdReview(TimeStampedModel):
    user_request = models.ForeignKey(RentalRequest, on_delete=models.CASCADE, related_name='user_request')
    review_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='review_user')
    owner_user = models.ForeignKey(UserBusinessProfile, on_delete=models.CASCADE, related_name='owner')
    rating = models.IntegerField(default=0)
    feedback = models.TextField()

    class Meta:
        verbose_name_plural = "Ad Reviews"
        verbose_name = "Ad Review"

    def save(self, *args, **kwargs):
        if not self.pk:
            request_query = RentalRequest.objects.get(id=self.user_request.id)
            request_query.is_review = True
            request_query.save()

            user_profile_rating = UserBusinessProfile.objects.get(id=self.owner_user.id)
            user_profile_rating.total_reviews = int(user_profile_rating.total_reviews + 1)
            user_profile_rating.total_ratings = float(
                (float(user_profile_rating.total_ratings) + float(self.rating)) / user_profile_rating.total_reviews)
            user_profile_rating.save()

            ad_rating = AdListing.objects.get(id=self.user_request.ad_list.id)
            ad_rating.total_reviews = int(ad_rating.total_reviews + 1)
            ad_rating.total_ratings = float(
                (float(ad_rating.total_ratings) + float(self.rating)) / ad_rating.total_reviews)
            ad_rating.save()

        super().save(**kwargs)

    def __str__(self):
        return f"{self.review_user.email} - {self.rating}"


