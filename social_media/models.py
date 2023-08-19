import os
import uuid

from django.db import models
from django.db.models.signals import post_save
from django.utils.text import slugify

from social_media_api import settings
from user.models import User

from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFit


class BaseModel(models.Model):
    """Base model for the application. Uses UUID for pk."""

    id = models.UUIDField(
        primary_key=True,
        editable=False,
        default=uuid.uuid4,
    )

    class Meta:
        """Metadata."""

        abstract = True


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
        f"{slugify(instance.user.first_name)}-"
        f"{slugify(instance.user.last_name)}-"
        f"{uuid.uuid4()}.{extension}",
    )


def image_file_path(instance, filename):
    _, extension = os.path.splitext(filename)
    return os.path.join(
        f"user-{instance.user.id}/images",
        f"{slugify(instance.user.first_name)}-"
        f"{slugify(instance.user.last_name)}-"
        f"{uuid.uuid4()}.{extension}",
    )


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile"
    )
    profile_picture = models.ImageField(
        default="default_profile_picture.png",
        upload_to=profile_picture_file_path,
    )
    bio = models.CharField(max_length=255, blank=True)
    location = models.CharField(max_length=65, blank=True)
    follows = models.ManyToManyField(
        "self", related_name="followed_by", symmetrical=False, blank=True
    )

    @property
    def full_name(self):
        """Returns the user's full name."""
        return "%s %s" % (self.user.first_name, self.user.last_name)

    @property
    def num_follows(self):
        """Returns the user followed other user number."""
        return self.follows.count() - 1

    @property
    def num_followed_by(self):
        """Returns the user followed by other user number."""
        return self.followed_by.count() - 1

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"


class HashTag(BaseModel):
    name = models.CharField(max_length=65, blank=False)

    def __str__(self):
        return self.name


class Post(BaseModel):
    """A post posted by a user."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="Created By",
        on_delete=models.CASCADE,
        related_name="posts",
    )

    content = models.TextField()
    image = ProcessedImageField(
        upload_to=image_file_path,
        format="JPEG",
        options={"quality": 90},
        processors=[ResizeToFit(width=1200, height=1200)],
        blank=True,
        null=True,
    )
    hashtag = models.ManyToManyField(HashTag, related_name="hashtags")
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    schedule_create = models.DateTimeField(blank=True, null=True)

    @property
    def num_likes(self):
        """Returns number of likes."""
        return self.likes.count()

    @property
    def num_comments(self):
        """Returns number of comments."""
        return self.comments.count()

    def __str__(self):
        return f"Post id: {self.id}, created: {self.date_created} "

    class Meta:
        ordering = ["-date_created"]


class Like(BaseModel):
    """A 'like' on a post."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="likes"
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="likes"
    )

    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user}"

    class Meta:
        unique_together = (("user", "post"),)
        ordering = ["-date_created"]


class Comment(BaseModel):
    """A comment on a post."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="comments"
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="comments"
    )

    content = models.TextField(max_length=2000)

    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user}: {self.content}"

    class Meta:
        ordering = ["-date_created"]
