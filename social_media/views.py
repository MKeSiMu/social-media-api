from rest_framework import viewsets, mixins, generics, status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from social_media.models import Profile, Post, Like, Comment
from social_media.permissions import IsOwnerOrReadOnly
from social_media.serializers import (
    ProfileSerializer,
    ProfileListSerializer,
    # UpdateProfileSerializer,
    FollowUnfollowProfileSerializer,
    PostSerializer,
    PostDetailSerializer,
    LikeSerializer,
    PostListSerializer,
    CommentSerializer,
    LikeUnlikePostSerializer,
    ProfileDetailSerializer,
    LikeDetailSerializer,
    CommentDetailSerializer
)


class ProfileViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet
):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly, )

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
                # .exclude(user=self.request.user)
            )
            return queryset

        return queryset

    def get_serializer_class(self):
        if self.action in ("update", "partial_update"):
            return ProfileDetailSerializer

        if self.action in ("list", "user_follows"):
            return ProfileListSerializer

        if self.action == "follow_unfollow":
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

    @action(methods=["POST"], detail=False, url_path="(?P<pk>[^/.]+)/follow-unfollow")
    def follow_unfollow(self, request, pk):
        """Endpoint for follow/unfollow specific profile"""
        user_profile = request.user.profile
        follow_profile = Profile.objects.select_related("user").get(id=pk)

        try:
            follow_profile.followed_by.get(user=user_profile.user)
        except follow_profile.DoesNotExist:

            user_profile.follows.add(follow_profile)
            return Response(
                {
                    'message': f"Now you are following "
                               f"{follow_profile.user}"
                },
                status=status.HTTP_201_CREATED
            )

        user_profile.follows.remove(follow_profile)
        return Response(
            {
                'message': f"You are no longer following "
                           f"{follow_profile.user}"
            },
            status=status.HTTP_204_NO_CONTENT
        )


# class ProfileRetrieveUpdateAPIView(generics.RetrieveUpdateAPIView):
#     serializer_class = UpdateProfileSerializer
#
#     def get_object(self):
#         return (
#             Profile.objects.select_related("user")
#             .get(user=self.request.user)
#         )


class LikeViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    queryset = Like.objects.all()
    serializer_class = LikeSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly,)

    def get_queryset(self):
        queryset = (
            self.queryset
            .select_related("user", "post")
            .filter(user=self.request.user)
        )
        return queryset

    def get_serializer_class(self):
        if self.action == "retrieve":
            return LikeDetailSerializer

        return LikeSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly,)

    def get_queryset(self):
        queryset = (
            self.queryset
            .select_related("user", "post")
            .filter(user=self.request.user)
        )
        return queryset

    def get_serializer_class(self):
        if self.action in ("retrieve", "update"):
            return CommentDetailSerializer

        return CommentSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly,)

    @staticmethod
    def _params_to_list(qs):
        """Converts a str to list of strings"""
        return [hashtag_name for hashtag_name in qs.split(",")]

    def get_queryset(self):
        queryset = self.queryset

        hashtags = self.request.query_params.get("hashtags")

        if hashtags:
            hashtag_list = self._params_to_list(hashtags)
            queryset = (
                queryset
                .filter(hashtag__name__in=hashtag_list)
            )

        if self.action == "list":
            queryset = (
                queryset
                .select_related("user")
                .prefetch_related("comments", "likes", "hashtag")
                .filter(user__profile__in=self.request.user.profile.follows.all())
            )
            return queryset

        if self.action == "retrieve":
            queryset = (
                queryset
                .select_related("user")
                .prefetch_related("comments__user", "likes__user", "hashtag")
            )
            return queryset

        return queryset.distinct()

    def get_serializer_class(self):
        if self.action in ("list", "create"):
            return PostListSerializer

        if self.action in ("retrieve", "update"):
            return PostDetailSerializer

        if self.action == "like_unlike":
            return LikeUnlikePostSerializer

        return PostSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(methods=["POST"], detail=False, url_path="(?P<pk>[^/.]+)/like-unlike")
    def like_unlike(self, request, pk):
        """Endpoint for like/unlike specific post"""
        post = get_object_or_404(Post.objects.select_related("user"), pk=pk)
        try:
            Like.objects.get(user=self.request.user, post=post)
        except Like.DoesNotExist:
            like = Like(post=post, user=self.request.user)
            like.save()
            post.likes.add(like)
            return Response(
                {
                    'message': f"You liked "
                               f"{post.user.first_name} {post.user.last_name}'s post"
                },
                status=status.HTTP_201_CREATED
            )

        Like.objects.select_related("user").get(user=self.request.user, post=post).delete()
        return Response(
            {
                'message': f"You unliked "
                           f"{post.user.first_name} {post.user.last_name}'s post"
            },
            status=status.HTTP_204_NO_CONTENT
        )
