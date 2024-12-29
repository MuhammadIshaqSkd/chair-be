from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView
from rest_framework_simplejwt.views import TokenViewBase
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated
)

from drf_spectacular.utils import extend_schema

from auths.api.serializers import (
    SignupSerializer,
    TokenObtainOverridePairSerializer
)
from auths.helper import get_token_for_user
from users.api.serializers import UserSerializer


@extend_schema(tags=['Auths'])
class RegistrationsAPIView(CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = SignupSerializer

    def post(self, request, *args, **kwargs):
        data = request.data

        # Validate and save user data
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Generate token and prepare response data
        payload = get_token_for_user(user)
        response_data = {**serializer.data, "token": payload["access"]}
        return Response(response_data, status.HTTP_201_CREATED)


@extend_schema(tags=['Auths'])
class MyTokenObtainPairView(TokenViewBase):
    """
    Takes a set of user credentials and returns access and refresh JSON web
    token pair to prove the authentication of those credentials.
    """
    serializer_class = TokenObtainOverridePairSerializer

@extend_schema(tags=['Auths'])
class UserRetrieveUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer


    def get(self, request, *args, **kwargs):
        user = request.user
        response_data = {}
        # Serialize user data and update the response
        serializer = self.serializer_class(user)
        response_data.update(serializer.data)

        return Response(response_data, status=status.HTTP_200_OK)
