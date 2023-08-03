from rest_framework import viewsets, mixins, generics, status
from rest_framework.decorators import action
from rest_framework.response import Response

from social_media.models import Profile
from social_media.serializers import (
    ProfileSerializer,
    ProfileListSerializer,
    UpdateProfileSerializer,
    FollowUnfollowProfileSerializer
)


class ProfileViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer

    def get_queryset(self):
        queryset = self.queryset

        username = self.request.query_params.get("username")
        first_name = self.request.query_params.get("first_name")
        last_name = self.request.query_params.get("last_name")

        if username:
            queryset = queryset.filter(user__username__icontains=username)

        if first_name:
            queryset = queryset.filter(user__first_name__icontains=first_name)

        if last_name:
            queryset = queryset.filter(user__last_name__icontains=last_name)

        if self.action in ("list", "retrieve"):
            queryset = (
                queryset
                .select_related("user")
                .prefetch_related("follows", "followed_by")
                .exclude(user=self.request.user)
            )
            return queryset

        return queryset

    def get_serializer_class(self):
        if self.action in ("list", "user_follows"):
            return ProfileListSerializer

        if self.action in ("follow", "unfollow"):
            return FollowUnfollowProfileSerializer

        return ProfileSerializer

    @action(methods=["GET"], detail=False, url_path="user-followed-by")
    def user_followed_by(self, request):
        return Response(
            ProfileListSerializer(
                Profile.objects.select_related("user")
                .get(user=request.user)
                .followed_by
                .select_related("user")
                .prefetch_related("followed_by", "follows")
                .exclude(id=self.request.user.profile.id), many=True).data,
            status=status.HTTP_200_OK
        )

    @action(methods=["GET"], detail=False, url_path="user-follows")
    def user_follows(self, request):
        return Response(
            ProfileListSerializer(
                Profile.objects.select_related("user")
                .get(user=request.user)
                .follows
                .select_related("user")
                .prefetch_related("followed_by", "follows")
                .exclude(id=self.request.user.profile.id), many=True).data,
            status=status.HTTP_200_OK
        )

    @action(methods=["POST"], detail=False, url_path="follow/(?P<pk>[^/.]+)")
    def follow(self, request, pk):
        """Endpoint for follow specific profile"""
        user_profile = request.user.profile
        follow_profile = Profile.objects.get(id=pk)
        user_profile.follows.add(follow_profile)
        return Response(
            {"message": f"Now you are following {follow_profile.user}"},
            status=status.HTTP_200_OK
        )

    @action(methods=["POST"], detail=False, url_path="unfollow/(?P<pk>[^/.]+)")
    def unfollow(self, request, pk):
        """Endpoint for unfollow specific profile"""
        user_profile = request.user.profile
        followed_profile = Profile.objects.get(id=pk)
        user_profile.follows.remove(followed_profile)
        return Response(
            {
                'message': f"You are no longer following "
                           f"{followed_profile.user}"
            },
            status=status.HTTP_200_OK
        )


class ProfileRetrieveUpdateAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = UpdateProfileSerializer

    def get_object(self):
        return (
            Profile.objects.select_related("user")
            .get(user=self.request.user)
        )
