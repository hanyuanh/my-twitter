from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db import models
from likes.models import Like
from utils.time_helpers import utc_now
from tweets.constants import TweetPhotoStatus, TWEET_PHOTO_STATUS_CHOICES

class Tweet(models.Model):
    # If there is foreign key, set null
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        help_text='who posts this tweet',
    )
    # Memory is allocated by size of base 2
    content = models.CharField(max_length=255)
    # updated this var when created
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # index_together = ((tup1), (tup2), (tup3), ...)
        index_together = (('user', 'created_at'), )

    @property
    def hours_to_now(self):
        # No timezone info in datetime.now. UTC timezone needed
        return (utc_now() - self.created_at).seconds // 3600

    @property
    def like_set(self):
        return Like.objects.filter(
            content_type=ContentType.objects.get_for_model(Tweet),
            object_id=self.id,
        ).order_by('-created_at')

    def __str__(self):
        # Showing return content when print(tweet instance) is called
        return f'{self.created_at} {self.user}: {self.content}'


class TweetPhoto(models.Model):
    # the tweet which the photo is attached to
    tweet = models.ForeignKey(Tweet, on_delete=models.SET_NULL, null=True)

    # user who upload the photo
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)

    file = models.FileField()
    order = models.IntegerField(default=0)

    # photo status for censorship
    status = models.IntegerField(
        default=TweetPhotoStatus.PENDING,
        choices=TWEET_PHOTO_STATUS_CHOICES,
    )

    # soft delete mark
    has_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        index_together = (
            ('user', 'created_at'),
            ('has_deleted', 'created_at'),
            ('status', 'created_at'),
            ('tweet', 'order'),
        )

    def __str__(self):
        return f'{self.tweet_id}: {self.file}'