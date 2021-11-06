from notifications.models import Notification
from testing.testcases import TestCase


COMMENT_URL = '/api/comments/'
LIKE_URL = '/api/likes/'
NOTIFICATION_URL = '/api/notifications/'


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


class NotificationApiTests(TestCase):

    def setUp(self):
        self.hanyuan, self.hanyuan_client = self.create_user_and_client('hanyuan')
        self.eric, self.eric_client = self.create_user_and_client('eric')
        self.hanyuan_tweet = self.create_tweet(self.hanyuan)

    def test_unread_count(self):
        self.eric_client.post(LIKE_URL, {
            'content_type': 'tweet',
            'object_id': self.hanyuan_tweet.id,
        })

        url = '/api/notifications/unread-count/'
        response = self.hanyuan_client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['unread_count'], 1)

        comment = self.create_comment(self.hanyuan, self.hanyuan_tweet)
        self.eric_client.post(LIKE_URL, {
            'content_type': 'comment',
            'object_id': comment.id,
        })
        response = self.hanyuan_client.get(url)
        self.assertEqual(response.data['unread_count'], 2)
        response = self.eric_client.get(url)
        self.assertEqual(response.data['unread_count'], 0)

    def test_mark_all_as_read(self):
        self.eric_client.post(LIKE_URL, {
            'content_type': 'tweet',
            'object_id': self.hanyuan_tweet.id,
        })
        comment = self.create_comment(self.hanyuan, self.hanyuan_tweet)
        self.eric_client.post(LIKE_URL, {
            'content_type': 'comment',
            'object_id': comment.id,
        })

        unread_url = '/api/notifications/unread-count/'
        response = self.hanyuan_client.get(unread_url)
        self.assertEqual(response.data['unread_count'], 2)

        mark_url = '/api/notifications/mark-all-as-read/'
        response = self.hanyuan_client.get(mark_url)
        self.assertEqual(response.status_code, 405)

        # eric can not mark hanyuan's notifications as read
        response = self.eric_client.post(mark_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['marked_count'], 0)
        response = self.hanyuan_client.get(unread_url)
        self.assertEqual(response.data['unread_count'], 2)

        # hanyuan can mark his notifications as read
        response = self.hanyuan_client.post(mark_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['marked_count'], 2)
        response = self.hanyuan_client.get(unread_url)
        self.assertEqual(response.data['unread_count'], 0)

    def test_list(self):
        self.eric_client.post(LIKE_URL, {
            'content_type': 'tweet',
            'object_id': self.hanyuan_tweet.id,
        })
        comment = self.create_comment(self.hanyuan, self.hanyuan_tweet)
        self.eric_client.post(LIKE_URL, {
            'content_type': 'comment',
            'object_id': comment.id,
        })

        # 匿名用户无法访问 api
        response = self.anonymous_client.get(NOTIFICATION_URL)
        self.assertEqual(response.status_code, 403)
        # eric 看不到任何 notifications
        response = self.eric_client.get(NOTIFICATION_URL)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 0)
        # hanyuan 看到两个 notifications
        response = self.hanyuan_client.get(NOTIFICATION_URL)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 2)
        # 标记之后看到一个未读
        notification = self.hanyuan.notifications.first()
        notification.unread = False
        notification.save()
        response = self.hanyuan_client.get(NOTIFICATION_URL)
        self.assertEqual(response.data['count'], 2)
        response = self.hanyuan_client.get(NOTIFICATION_URL, {'unread': True})
        self.assertEqual(response.data['count'], 1)
        response = self.hanyuan_client.get(NOTIFICATION_URL, {'unread': False})
        self.assertEqual(response.data['count'], 1)


    def test_update(self):
        # eric liked hanyuan's tweet
        self.eric_client.post(LIKE_URL, {
            'content_type': 'tweet',
            'object_id': self.hanyuan_tweet.id,
        })
        comment = self.create_comment(self.hanyuan, self.hanyuan_tweet)
        # eric liked hanyuan's comment
        self.eric_client.post(LIKE_URL, {
            'content_type': 'comment',
            'object_id': comment.id,
        })
        # hanyuan should get notification
        notification = self.hanyuan.notifications.first()

        url = '/api/notifications/{}/'.format(notification.id)
        # cannot use post, use put here
        response = self.eric_client.post(url, {'unread': False})
        self.assertEqual(response.status_code, 405)
        # return http 405 method not allow
        # Not allowed to change the status of others' notification
        response = self.anonymous_client.put(url, {'unread': False})
        self.assertEqual(response.status_code, 403)
        # queryset is based on current login user, so return 404 not found,
        # not 403
        response = self.eric_client.put(url, {'unread': False})
        self.assertEqual(response.status_code, 404)
        # tag it as read successfully
        response = self.hanyuan_client.put(url, {'unread': False})
        self.assertEqual(response.status_code, 200)
        unread_url = '/api/notifications/unread-count/'
        response = self.hanyuan_client.get(unread_url)
        self.assertEqual(response.data['unread_count'], 1)

        # re-tag it as unread
        response = self.hanyuan_client.put(url, {'unread': True})
        response = self.hanyuan_client.get(unread_url)
        self.assertEqual(response.data['unread_count'], 2)
        # must have param unread
        response = self.hanyuan_client.put(url, {'verb': 'newverb'})
        self.assertEqual(response.status_code, 400)
        # cannot change other info
        response = self.hanyuan_client.put(url, {'verb': 'newverb', 'unread': False})
        self.assertEqual(response.status_code, 200)
        notification.refresh_from_db() # reload data from db
        self.assertNotEqual(notification.verb, 'newverb')