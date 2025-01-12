from django.conf import settings
from django.views.static import serve
from django.urls import path, re_path
from rest_framework.routers import DefaultRouter

from ad_listing.api.views import (
    RequestReviewView,
    AdListingViewSet,
    RentalRequestView,
)
from auths.api.views import (
    RegistrationsAPIView,
    MyTokenObtainPairView,
    UserRetrieveUpdateAPIView,
)
from users.api.views import (
    UserRentalProfileViewSet,
    UpdateUserAccountTypeView,
    ConversationViewSet,
    MessageViewSet,
)

# Router setup
router = DefaultRouter()
router.register(r'rental-profile', UserRentalProfileViewSet, basename='user-rental-profile')
router.register(r'rental-request', RentalRequestView, basename='rental-request')
router.register(r'ad-listing', AdListingViewSet, basename='ad-listing')
router.register(r'request-review', RequestReviewView, basename='request-review')

router.register(r'conversation', ConversationViewSet, basename='conversation')
router.register(r'message', MessageViewSet, basename='message')


# URL Patterns
urlpatterns = [
    # Static and Media Files (use only in development)
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),

    # Auths
    path('register/', RegistrationsAPIView.as_view(), name='register'),
    path('login/', MyTokenObtainPairView.as_view(), name='login'),
    path('verify/token/', UserRetrieveUpdateAPIView.as_view(), name='verify/token/'),
    path('user/account-type/', UpdateUserAccountTypeView.as_view(), name='update-user-account-type'),

]

# Include router URLs
urlpatterns += router.urls
