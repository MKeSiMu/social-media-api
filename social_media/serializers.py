from rest_framework import serializers

from social_media.models import Profile, Post, HashTag, Like, Comment
from user.models import User
from user.serializers import UserSerializer


class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    first_name = serializers.CharField(source="user.first_name", read_only=True)
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
            "num_followed_by",
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
            "num_followed_by",
        )


class ProfileDetailSerializer(serializers.ModelSerializer):
    user = UserSerializer(required=True, many=False)

    class Meta:
        model = Profile
        fields = ("user", "profile_picture", "bio", "location")

    def update(self, instance, validated_data):
        user_data = validated_data.pop("user", None)
        user_email = self.data["user"]["email"]
        user = User.objects.get(email=user_email)

        user_serializer = UserSerializer(data=user_data)
        if user_serializer.is_valid():
            user_serializer.update(user, user_data)
        instance.save()
        return super(ProfileDetailSerializer, self).update(instance, validated_data)


class FollowUnfollowProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ()


class HashTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = HashTag
        fields = ("name",)


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ("id", "post", "content")
        read_only_fields = ("id",)


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = (
            "id",
            "user",
            "content",
            "image",
            "hashtag",
            "date_created",
            "date_updated",
        )
        read_only_fields = (
            "id",
            "user",
        )


class PostListSerializer(PostSerializer):
    hashtag = HashTagSerializer(many=True)
    user = serializers.StringRelatedField()

    class Meta:
        model = Post
        fields = (
            "id",
            "user",
            "content",
            "image",
            "hashtag",
            "num_likes",
            "num_comments",
            "date_created",
            "date_updated",
            "schedule_create",
        )
        read_only_fields = (
            "id",
            "user",
        )

    def create(self, validated_data):
        hashtags_data = validated_data.pop("hashtag")

        post = Post.objects.create(**validated_data)

        for hashtag in hashtags_data:
            obj, ht = HashTag.objects.get_or_create(name=hashtag.get("name"))

            if not ht:
                post.hashtag.add(obj)

            else:
                obj.save()
                post.hashtag.add(obj)

        post.save()
        return post


class PostDetailSerializer(serializers.ModelSerializer):
    likes = serializers.StringRelatedField(many=True, read_only=True, required=False)
    comments = CommentSerializer(many=True, read_only=True)
    hashtag = HashTagSerializer(many=True, required=False)

    class Meta:
        model = Post
        fields = (
            "id",
            "user",
            "content",
            "image",
            "hashtag",
            "likes",
            "comments",
            "date_created",
            "date_updated",
        )
        read_only_fields = (
            "id",
            "user",
            "likes",
            "comments",
            "date_created",
            "date_updated",
        )

    def update(self, instance, validated_data):
        hashtags_data = validated_data.pop("hashtag", [])
        Post.objects.filter(id=instance.id).update(**validated_data)
        hashtag_objs = [
            HashTag.objects.get_or_create(name=hashtag.get("name"))[0]
            for hashtag in hashtags_data
        ]

        instance.refresh_from_db()
        instance.hashtag.set(hashtag_objs)
        instance.save()

        return instance


class LikeUnlikePostSerializer(PostDetailSerializer):
    class Meta:
        model = Post
        fields = ()


class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = (
            "id",
            "post",
        )
        read_only_fields = ("id",)


class LikeDetailSerializer(LikeSerializer):
    class Meta:
        model = Like
        fields = ("id", "post", "date_created")
        read_only_fields = (
            "id",
            "post",
        )


class CommentDetailSerializer(CommentSerializer):
    class Meta:
        model = Comment
        fields = ("id", "post", "content", "date_created")
        read_only_fields = (
            "id",
            "post",
        )
