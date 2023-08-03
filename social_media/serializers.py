from rest_framework import serializers

from social_media.models import Profile
from user.models import User
from user.serializers import UserSerializer


class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    first_name = serializers.CharField(
        source="user.first_name",
        read_only=True
    )
    last_name = serializers.CharField(source="user.last_name", read_only=True)

    class Meta:
        model = Profile
        fields = (
            "id",
            "username",
            "first_name",
            "full_name",
            "last_name",
            "profile_picture",
            "bio",
            "location",
            "num_follows",
            "num_followed_by"
        )


class ProfileListSerializer(ProfileSerializer):

    class Meta:
        model = Profile
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "full_name",
            "profile_picture",
            "num_follows",
            "num_followed_by"
        )


class FollowUnfollowProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ()


class UpdateProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(required=True, many=False)

    class Meta:
        model = Profile
        fields = ("user", "profile_picture", "bio", "location")

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user')
        user_email = self.data['user']['email']
        user = User.objects.get(email=user_email)

        user_serializer = UserSerializer(data=user_data)
        if user_serializer.is_valid():
            user_serializer.update(user, user_data)
        instance.save()
        return super(
            UpdateProfileSerializer, self
        ).update(instance, validated_data)
