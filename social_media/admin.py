from django.contrib import admin

from social_media.models import Profile, Post


class ProfileInline(admin.StackedInline):
    model = Profile


admin.site.register(Post)
