from __future__ import absolute_import, unicode_literals

from celery import shared_task

from social_media.models import Post, HashTag


@shared_task
def schedule_post_creation(content, image, hashtags, user_id):
    post = Post.objects.create(
        content=content,
        image=image,
        user_id=user_id
    )

    hashtag_objs = [
        HashTag.objects.get_or_create(name=hashtag.get("name"))[0]
        for hashtag in hashtags
    ]

    post.hashtag.set(hashtag_objs)

    post.save()
    return post.id
