from django.conf import settings
from django.views.static import serve
from django.urls import path, re_path
from rest_framework.routers import DefaultRouter

from auths.api.views import (
    RegistrationsAPIView,
    MyTokenObtainPairView
)

# Router setup
router = DefaultRouter()

# URL Patterns
urlpatterns = [
    # Static and Media Files (use only in development)
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),

    # Auths
    path('register/', RegistrationsAPIView.as_view(), name='register'),
    path('login/', MyTokenObtainPairView.as_view(), name='login'),
]

# Include router URLs
urlpatterns += router.urls
