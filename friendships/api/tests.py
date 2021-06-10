from friendships.models import Friendship
from rest_framework.test import APIClient
from testing.testcases import TestCase


FOLLOW_URL = '/api/friendships/{}/follow/'
UNFOLLOW_URL = '/api/friendships/{}/unfollow/'
FOLLOWERS_URL = '/api/friendships/{}/followers/'
FOLLOWINGS_URL = '/api/friendships/{}/followings/'


class FriendshipApiTests(TestCase):

    def setUp(self):
        # create
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

    def test_follow(self):
        # generate a correct follow url
        url = FOLLOW_URL.format(self.hanyuan.id)

        # need to login to follow someone
        response = self.anonymous_client.post(url)
        self.assertEqual(response.status_code, 403)
        # cannot use get method to follow
        response = self.eric_client.get(url)
        self.assertEqual(response.status_code, 405)
        # cannot follow yourself
        response = self.hanyuan_client.post(url)
        self.assertEqual(response.status_code, 400)
        # follow succeeds
        response = self.eric_client.post(url)
        self.assertEqual(response.status_code, 201)
        self.assertEqual('created_at' in response.data, True)
        self.assertEqual('user' in response.data, True)
        self.assertEqual('user' in response.data, True)
        self.assertEqual(response.data['user']['id'], self.hanyuan.id)
        self.assertEqual(response.data['user']['username'], self.hanyuan.username)
        # duplicate detected, return 400
        response = self.eric_client.post(url)
        self.assertEqual(response.status_code, 400)
        # 反向关注会创建新的数据
        count = Friendship.objects.count()
        response = self.hanyuan_client.post(FOLLOW_URL.format(self.eric.id))
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Friendship.objects.count(), count + 1)

    def test_unfollow(self):
        url = UNFOLLOW_URL.format(self.hanyuan.id)

        # login to unfollow
        response = self.anonymous_client.post(url)
        self.assertEqual(response.status_code, 403)
        # cannot use get to unfollow
        response = self.eric_client.get(url)
        self.assertEqual(response.status_code, 405)
        # cannot unfollow yourself
        response = self.hanyuan_client.post(url)
        self.assertEqual(response.status_code, 400)
        # unfollow succeeds
        Friendship.objects.create(from_user=self.eric, to_user=self.hanyuan)
        count = Friendship.objects.count()
        response = self.eric_client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['deleted'], 1)
        self.assertEqual(Friendship.objects.count(), count - 1)
        # If the relationship has not followed, then unfollow method should be
        # invalid. Here return status code 200 with ['deleted'] = 0.
        count = Friendship.objects.count()
        response = self.eric_client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['deleted'], 0)
        self.assertEqual(Friendship.objects.count(), count)

    def test_followings(self):
        url = FOLLOWINGS_URL.format(self.eric.id)
        # post is not allowed
        response = self.anonymous_client.post(url)
        self.assertEqual(response.status_code, 405)
        # get is ok
        response = self.anonymous_client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['followings']), 3)
        # by the reverse order of the timestamp
        ts0 = response.data['followings'][0]['created_at']
        ts1 = response.data['followings'][1]['created_at']
        ts2 = response.data['followings'][2]['created_at']
        self.assertEqual(ts0 > ts1, True)
        self.assertEqual(ts1 > ts2, True)
        self.assertEqual(
            response.data['followings'][0]['user']['username'],
            'eric_following2',
        )
        self.assertEqual(
            response.data['followings'][1]['user']['username'],
            'eric_following1',
        )
        self.assertEqual(
            response.data['followings'][2]['user']['username'],
            'eric_following0',
        )

    def test_followers(self):
        url = FOLLOWERS_URL.format(self.eric.id)
        # post is not allowed
        response = self.anonymous_client.post(url)
        self.assertEqual(response.status_code, 405)
        # get is ok
        response = self.anonymous_client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['followers']), 2)
        # by the reverse order of timestamp
        ts0 = response.data['followers'][0]['created_at']
        ts1 = response.data['followers'][1]['created_at']
        self.assertEqual(ts0 > ts1, True)
        self.assertEqual(
            response.data['followers'][0]['user']['username'],
            'eric_follower1',
        )
        self.assertEqual(
            response.data['followers'][1]['user']['username'],
            'eric_follower0',
        )