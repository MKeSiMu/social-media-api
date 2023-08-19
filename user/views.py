from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from social_media.serializers import ProfileDetailSerializer
from user.serializers import UserSerializer


class UserCreateView(generics.CreateAPIView):
    serializer_class = UserSerializer


class ManageUserView(generics.RetrieveUpdateAPIView):
    serializer_class = ProfileDetailSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user.profile
