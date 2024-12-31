from django.conf import settings
from django.views.static import serve
from django.urls import path, re_path
from rest_framework.routers import DefaultRouter

from ad_listing.api.views import AdListingViewSet
from auths.api.views import (
    RegistrationsAPIView,
    MyTokenObtainPairView,
    UserRetrieveUpdateAPIView,
)
from users.api.views import UserRentalProfileViewSet

# Router setup
router = DefaultRouter()
router.register(r'rental-profile', UserRentalProfileViewSet, basename='user-rental-profile')
router.register(r'ad-listing', AdListingViewSet, basename='ad-listing')

# URL Patterns
urlpatterns = [
    # Static and Media Files (use only in development)
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),

    # Auths
    path('register/', RegistrationsAPIView.as_view(), name='register'),
    path('login/', MyTokenObtainPairView.as_view(), name='login'),
    path('verify/token/', UserRetrieveUpdateAPIView.as_view(), name='verify/token/'),

]

# Include router URLs
urlpatterns += router.urls
