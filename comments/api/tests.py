from comments.models import Comment
from django.utils import timezone
from rest_framework.test import APIClient
from testing.testcases import TestCase


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

    def test_destroy(self):
        comment = self.create_comment(self.hanyuan, self.tweet)
        url = '{}{}/'.format(COMMENT_URL, comment.id)

        # invalid if anonymous user
        response = self.anonymous_client.delete(url)
        self.assertEqual(response.status_code, 403)

        # invalid if not the owner of the comment
        response = self.eric_client.delete(url)
        self.assertEqual(response.status_code, 403)

        # valid if the owner deletes
        count = Comment.objects.count()
        response = self.hanyuan_client.delete(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Comment.objects.count(), count - 1)

    def test_update(self):
        comment = self.create_comment(self.hanyuan, self.tweet, 'original')
        another_tweet = self.create_tweet(self.eric)
        url = '{}{}/'.format(COMMENT_URL, comment.id)

        # When use put
        # invalid if anonymous user
        response = self.anonymous_client.put(url, {'content': 'new'})
        self.assertEqual(response.status_code, 403)
        # invalid if not owner
        response = self.eric_client.put(url, {'content': 'new'})
        self.assertEqual(response.status_code, 403)
        comment.refresh_from_db()
        self.assertNotEqual(comment.content, 'new')
        # only update the content, cannot update anything else
        before_updated_at = comment.updated_at
        before_created_at = comment.created_at
        now = timezone.now()
        response = self.hanyuan_client.put(url, {
            'content': 'new',
            'user_id': self.eric.id,
            'tweet_id': another_tweet.id,
            'created_at': now,
        })
        self.assertEqual(response.status_code, 200)
        comment.refresh_from_db()
        self.assertEqual(comment.content, 'new')
        self.assertEqual(comment.user, self.hanyuan)
        self.assertEqual(comment.tweet, self.tweet)
        self.assertEqual(comment.created_at, before_created_at)
        self.assertNotEqual(comment.created_at, now)
        self.assertNotEqual(comment.updated_at, before_updated_at)