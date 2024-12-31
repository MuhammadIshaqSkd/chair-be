from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from ad_listing.models import AdListing
from auths.models import UserBusinessProfile
from ad_listing.api.serializers import AdListingSerializer, AdListImageSerializer


# Create your views here.

class AdListingViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = AdListingSerializer
    queryset = AdListing.objects.all()

    def create(self, request, *args, **kwargs):
        user = request.user
        business_profile = UserBusinessProfile.objects.filter(user=user)
        if not business_profile.exists():
            return Response(
                "Business profile does not exist for this user.",
                status=status.HTTP_400_BAD_REQUEST
            )
        new_data = request.data.copy()
        new_data.pop("ad_images", "[]")
        new_data['user'] = business_profile.first().id
        ad_list_serializer = self.get_serializer(data=new_data)
        ad_list_serializer.is_valid(raise_exception=True)
        ad_list__ins = ad_list_serializer.save()

        images = request.data.getlist("ad_images")
        img_ids = []
        for image in images:
            data = {"image": image}
            post_ser = AdListImageSerializer(data=data)
            post_ser.is_valid(raise_exception=True)
            post_ins = post_ser.save()
            img_ids.append(post_ins.id)
            ad_list__ins.ad_images.set(img_ids)
        ad_list__ins.save()
        return Response(ad_list_serializer.data, status=status.HTTP_201_CREATED)