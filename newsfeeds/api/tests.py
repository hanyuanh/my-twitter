from newsfeeds.models import NewsFeed
from friendships.models import Friendship
from rest_framework.test import APIClient
from testing.testcases import TestCase


NEWSFEEDS_URL = '/api/newsfeeds/'
POST_TWEETS_URL = '/api/tweets/'
FOLLOW_URL = '/api/friendships/{}/follow/'


class NewsFeedApiTests(TestCase):

    def setUp(self):
        self.hanyuan = self.create_user('hanyuan')
        self.hanyuan_client = APIClient()
        self.hanyuan_client.force_authenticate(self.hanyuan)

        self.eric = self.create_user('eric')
        self.eric_client = APIClient()
        self.eric_client.force_authenticate(self.eric)

        # create followings and followers for eric
        for i in range(2):
            follower = self.create_user('eric_follower{}'.format(i))
            Friendship.objects.create(from_user=follower, to_user=self.eric)
        for i in range(3):
            following = self.create_user('eric_following{}'.format(i))
            Friendship.objects.create(from_user=self.eric, to_user=following)

    def test_list(self):
        # need to login
        response = self.anonymous_client.get(NEWSFEEDS_URL)
        self.assertEqual(response.status_code, 403)
        # cannot use post
        response = self.hanyuan_client.post(NEWSFEEDS_URL)
        self.assertEqual(response.status_code, 405)
        # At the beginning there is no newsfeed
        response = self.hanyuan_client.get(NEWSFEEDS_URL)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['newsfeeds']), 0)
        # I can see my own tweet
        self.hanyuan_client.post(POST_TWEETS_URL, {'content': 'Hello World'})
        response = self.hanyuan_client.get(NEWSFEEDS_URL)
        self.assertEqual(len(response.data['newsfeeds']), 1)
        # can see other's tweets after following
        self.hanyuan_client.post(FOLLOW_URL.format(self.eric.id))
        response = self.eric_client.post(POST_TWEETS_URL, {
            'content': 'Hello Twitter',
        })
        posted_tweet_id = response.data['id']
        response = self.hanyuan_client.get(NEWSFEEDS_URL)
        self.assertEqual(len(response.data['newsfeeds']), 2)
        self.assertEqual(response.data['newsfeeds'][0]['tweet']['id'], posted_tweet_id)