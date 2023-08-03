from django.urls import path, include
from rest_framework import routers

from social_media.views import ProfileViewSet, ProfileRetrieveUpdateAPIView

router = routers.DefaultRouter()
router.register("profiles", ProfileViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path(
        "user-profile/",
        ProfileRetrieveUpdateAPIView.as_view(),
        name="user-profile"
    ),
]

app_name = "social-media"
