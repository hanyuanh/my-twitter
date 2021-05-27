from django.db import models
from django.contrib.auth.models import User


class Friendship(models.Model):
    # from_user follows to_user
    from_user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='following_friendship_set',
    )
    to_user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='follower_friendship_set',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        index_together = (
            # get all of my followings, ordering by follow timestamp
            ('from_user_id', 'created_at'),
            # get all of my followers, ordering by follow timestamp
            ('to_user_id', 'created_at'),
        )
        # this from_user follow to_user relationship should be unique, database
        # should only store once. This code will return error if multiple
        # relationships create (e.g. someone clicks follow button too fast)
        unique_together = (('from_user_id', 'to_user_id'),)

    def __str__(self):
        return '{} followed {}'.format(self.from_user_id, self.to_user_id)