from notifications.models import Notification
from testing.testcases import TestCase


COMMENT_URL = '/api/comments/'
LIKE_URL = '/api/likes/'


class NotificationTests(TestCase):

    def setUp(self):
        self.hanyuan, self.hanyuan_client = self.create_user_and_client('hanyuan')
        self.eric, self.eric_client = self.create_user_and_client('eric')
        self.eric_tweet = self.create_tweet(self.eric)

    def test_comment_create_api_trigger_notification(self):
        self.assertEqual(Notification.objects.count(), 0)
        tmp = self.hanyuan_client.post(COMMENT_URL, {
            'tweet_id': self.eric_tweet.id,
            'content': 'a ha',
        })
        self.assertEqual(Notification.objects.count(), 1)

    def test_like_create_api_trigger_notification(self):
        self.assertEqual(Notification.objects.count(), 0)
        self.hanyuan_client.post(LIKE_URL, {
            'content_type': 'tweet',
            'object_id': self.eric_tweet.id,
        })
        self.assertEqual(Notification.objects.count(), 1)