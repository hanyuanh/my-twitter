from comments.models import Comment
from django.contrib.auth.models import User
from django.test import TestCase as DjangoTestCase  # to avoid name duplicate
from rest_framework.test import APIClient
from tweets.models import Tweet


class TestCase(DjangoTestCase):

    @property
    def anonymous_client(self):
        # create a variable '_anonymous_client' in self (in instance level
        # cache) to store the APIClient() when first time using it.
        if hasattr(self, '_anonymous_client'):
            return self._anonymous_client
        self._anonymous_client = APIClient()
        return self._anonymous_client

    def create_user(self, username, email=None, password=None):
        if password is None:
            password = 'generic password'
        if email is None:
            email = f'{username}@twitter.com'
        # cannot use User.objects.create()
        # password needs to encrypt, username and email need to normalize
        return User.objects.create_user(username, email, password)

    def create_tweet(self, user, content=None):
        if content is None:
            content = 'default tweet content'
        return Tweet.objects.create(user=user, content=content)

    def create_comment(self, user, tweet, content=None):
        if content is None:
            content = 'default comment content'
        return Comment.objects.create(user=user, tweet=tweet, content=content)