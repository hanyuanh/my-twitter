from rest_framework.test import APIClient
from testing.testcases import TestCase
from tweets.models import Tweet


# should end with '/', otherwise 301 redirect
TWEET_LIST_API = '/api/tweets/'
TWEET_CREATE_API = '/api/tweets/'
TWEET_RETRIEVE_API = '/api/tweets/{}/'


class TweetApiTests(TestCase):

    def setUp(self):
        self.hanyuan = self.create_user('hanyuan', 'hanyuan@twitter.com')
        self.tweets1 = [
            self.create_tweet(self.hanyuan)
            for i in range(3)
        ]
        self.hanyuan_client = APIClient()
        #
        self.hanyuan_client.force_authenticate(self.hanyuan)

        self.eric = self.create_user('eric', 'eric@twitter.com')
        self.tweets2 = [
            self.create_tweet(self.eric)
            for i in range(2)
        ]

    def test_list_api(self):
        # must have user_id
        response = self.anonymous_client.get(TWEET_LIST_API)
        self.assertEqual(response.status_code, 400)

        # normal request
        response = self.anonymous_client.get(TWEET_LIST_API, {'user_id': self.hanyuan.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['tweets']), 3)
        response = self.anonymous_client.get(TWEET_LIST_API, {'user_id': self.eric.id})
        self.assertEqual(len(response.data['tweets']), 2)
        # the ordering in response.data: latest tweet is at the head
        self.assertEqual(response.data['tweets'][0]['id'], self.tweets2[1].id)
        self.assertEqual(response.data['tweets'][1]['id'], self.tweets2[0].id)

    def test_create_api(self):
        # must login
        response = self.anonymous_client.post(TWEET_CREATE_API)
        self.assertEqual(response.status_code, 403)

        # must have content
        response = self.hanyuan_client.post(TWEET_CREATE_API)
        self.assertEqual(response.status_code, 400)
        # content cannot be too short (>6)
        response = self.hanyuan_client.post(TWEET_CREATE_API, {'content': '1'})
        self.assertEqual(response.status_code, 400)
        # content cannot be too long (<140)
        response = self.hanyuan_client.post(TWEET_CREATE_API, {
            'content': '0' * 141
        })
        self.assertEqual(response.status_code, 400)

        # create a good tweet
        tweets_count = Tweet.objects.count()
        response = self.hanyuan_client.post(TWEET_CREATE_API, {
            'content': 'Hello World, this is my first tweet!'
        })
        self.assertEqual(response.status_code, 201)
        # check if it is from hanyuan
        self.assertEqual(response.data['user']['id'], self.hanyuan.id)
        # check if database is updated
        self.assertEqual(Tweet.objects.count(), tweets_count + 1)

    def test_retrieve(self):
        # tweet with id=-1 does not exist
        url = TWEET_RETRIEVE_API.format(-1)
        response = self.anonymous_client.get(url)
        self.assertEqual(response.status_code, 404)

        # pull comments along with tweets
        tweet = self.create_tweet(self.hanyuan)
        url = TWEET_RETRIEVE_API.format(tweet.id)
        response = self.anonymous_client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['comments']), 0)

        self.create_comment(self.eric, tweet, 'holy moly')
        self.create_comment(self.hanyuan, tweet, 'dope move')
        self.create_comment(self.hanyuan, self.create_tweet(self.eric), 'looks great')
        response = self.anonymous_client.get(url)
        self.assertEqual(len(response.data['comments']), 2)