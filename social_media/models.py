import os
import uuid

from django.db import models
from django.db.models.signals import post_save
from django.utils.text import slugify

from social_media_api import settings
from user.models import User


def create_profile(sender, instance, created, **kwargs):
    if created:
        user_profile = Profile(user=instance)
        user_profile.save()
        user_profile.follows.set([instance.profile.id])
        user_profile.save()


post_save.connect(create_profile, sender=User)


def profile_picture_file_path(instance, filename):
    _, extension = os.path.splitext(filename)
    return os.path.join(
        f"user-{instance.user.id}/profile_photo",
        f"{slugify(instance.user.first_name)}-{slugify(instance.user.last_name)}-{uuid.uuid4()}.{extension}",
    )


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    profile_picture = models.ImageField(
        default="default_profile_picture.png",
        upload_to=profile_picture_file_path,
    )
    bio = models.CharField(max_length=255, blank=True)
    location = models.CharField(max_length=65, blank=True)
    follows = models.ManyToManyField(
        "self", related_name="followed_by", symmetrical=False, blank=True
    )

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"
