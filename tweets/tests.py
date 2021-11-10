from testing.testcases import TestCase
from datetime import timedelta
from utils.time_helpers import utc_now
from tweets.models import TweetPhoto
from tweets.constants import TweetPhotoStatus


class TweetTests(TestCase):
    def setUp(self):
        self.hanyuan = self.create_user('hanyuan')
        self.tweet = self.create_tweet(self.hanyuan, content='Hanyuan tweets!')

    def test_hours_to_now(self):
        self.tweet.created_at = utc_now() - timedelta(hours=10)
        self.tweet.save()
        self.assertEqual(self.tweet.hours_to_now, 10)

    def test_like_set(self):
        self.create_like(self.hanyuan, self.tweet)
        self.assertEqual(self.tweet.like_set.count(), 1)

        self.create_like(self.hanyuan, self.tweet)
        self.assertEqual(self.tweet.like_set.count(), 1)

        eric = self.create_user('eric')
        self.create_like(eric, self.tweet)
        self.assertEqual(self.tweet.like_set.count(), 2)


    def test_create_photo(self):
        # test if photo object can be created successfully
        photo = TweetPhoto.objects.create(
            tweet=self.tweet,
            user=self.hanyuan,
        )
        self.assertEqual(photo.user, self.hanyuan)
        self.assertEqual(photo.status, TweetPhotoStatus.PENDING)
        self.assertEqual(self.tweet.tweetphoto_set.count(), 1)