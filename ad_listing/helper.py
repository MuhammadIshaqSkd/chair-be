from rest_framework.pagination import PageNumberPagination
from ad_listing.api.serializers import AdListImageSerializer

class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

def process_media(post_media):
    img_ids = []
    for image in post_media:
        data = {"image": image}
        list_img_ser = AdListImageSerializer(data=data)
        list_img_ser.is_valid(raise_exception=True)
        post_ins = list_img_ser.save()
        img_ids.append(post_ins.id)
    return img_ids