from django.contrib import admin

from social_media.models import Profile, Post, Like, Comment, HashTag


class ProfileInline(admin.StackedInline):
    model = Profile


class CommentInline(admin.StackedInline):
    model = Comment
    extra = 1


class LikeInline(admin.StackedInline):
    model = Like
    extra = 1


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    inlines = (CommentInline, LikeInline)


# admin.site.register(Post)
admin.site.register(Like)
admin.site.register(Comment)
admin.site.register(HashTag)
