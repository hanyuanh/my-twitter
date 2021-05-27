from django.db import models
from django.contrib.auth.models import User
from utils.time_helpers import utc_now


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

    def __str__(self):
        # Showing return content when print(tweet instance) is called
        return f'{self.created_at} {self.user}: {self.content}'
