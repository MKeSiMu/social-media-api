from django.contrib import admin

from social_media.models import Profile, Post, Like, Comment


class ProfileInline(admin.StackedInline):
    model = Profile


admin.site.register(Post)
admin.site.register(Like)
admin.site.register(Comment)
