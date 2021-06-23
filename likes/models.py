from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models


class Like(models.Model):
    # https://docs.djangoproject.com/en/3.1/ref/contrib/contenttypes/#generic-relations
    object_id = models.PositiveIntegerField() # comment id or tweet id
    content_type = models.ForeignKey(
        ContentType, # specifically what type the object is
        on_delete=models.SET_NULL,
        null=True,
    )
    # user liked content_object at created_at
    content_object = GenericForeignKey('content_type', 'object_id')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Here unique together will build an index
        # <user, content_type, object_id>. This index can also search different
        # objects that a certain user likes.
        # Therefore, this feature cannot be done if unique together changes to
        # <content_type, object_id, user>
        unique_together = (('user', 'content_type', 'object_id'),)
        # This index is to search all likes of a liked content_object, sorted by
        # timestamp
        index_together = (
            ('content_type', 'object_id', 'created_at'),
            ('user', 'content_type', 'created_at'),
        )
        # # can pull a list of tweets that the user has likes on. This feature
        # is just like like list in TikTok
        # index_together = (('user', 'content_type', 'created_at'),)

    def __str__(self):
        return '{} - {} liked {} {}'.format(
            self.created_at,
            self.user,
            self.content_type,
            self.object_id,
        )