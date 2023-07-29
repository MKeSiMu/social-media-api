from django.contrib import admin

from social_media.models import Profile


class ProfileInline(admin.StackedInline):
    model = Profile
