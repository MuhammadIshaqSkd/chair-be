from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView


class HealthCheckAPIView(APIView):
    permission_classes = [AllowAny]

    @staticmethod
    def get(request, *args, **kwargs):
        return Response({"status": "OK"})
