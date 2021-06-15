from testing.testcases import TestCase
from rest_framework.test import APIClient


COMMENT_URL = '/api/comments/'


class CommentApiTests(TestCase):

    def setUp(self):
        self.hanyuan = self.create_user('hanyuan')
        self.hanyuan_client = APIClient()
        self.hanyuan_client.force_authenticate(self.hanyuan)
        self.eric = self.create_user('eric')
        self.eric_client = APIClient()
        self.eric_client.force_authenticate(self.eric)

        self.tweet = self.create_tweet(self.hanyuan)

    def test_create(self):
        # An anonymous client cannot create comment
        response = self.anonymous_client.post(COMMENT_URL)
        self.assertEqual(response.status_code, 403)

        # invalid if there is no parameter
        response = self.hanyuan_client.post(COMMENT_URL)
        self.assertEqual(response.status_code, 400)

        # invalid if there is only with tweet_id
        response = self.hanyuan_client.post(COMMENT_URL, {'tweet_id': self.tweet.id})
        self.assertEqual(response.status_code, 400)

        # invalid if there is only with content
        response = self.hanyuan_client.post(COMMENT_URL, {'content': '1'})
        self.assertEqual(response.status_code, 400)

        # invalid if content is too long
        response = self.hanyuan_client.post(COMMENT_URL, {
            'tweet_id': self.tweet.id,
            'content': '1' * 141,   #a string of length 141
        })
        self.assertEqual(response.status_code, 400)
        self.assertEqual('content' in response.data['errors'], True)

        # valid only when tweet_id and content are filled
        response = self.hanyuan_client.post(COMMENT_URL, {
            'tweet_id': self.tweet.id,
            'content': '1',
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['user']['id'], self.hanyuan.id)
        self.assertEqual(response.data['tweet_id'], self.tweet.id)
        self.assertEqual(response.data['content'], '1')