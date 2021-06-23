from testing.testcases import TestCase


class CommentModelTests(TestCase):

    def setUp(self):
        self.hanyuan = self.create_user('hanyuan')
        self.tweet = self.create_tweet(self.hanyuan)
        self.comment = self.create_comment(self.hanyuan, self.tweet)

    def test_comment(self):
        self.assertNotEqual(self.comment.__str__(), None)

    def test_like_set(self):
        self.create_like(self.hanyuan, self.comment)
        self.assertEqual(self.comment.like_set.count(), 1)

        self.create_like(self.hanyuan, self.comment)
        self.assertEqual(self.comment.like_set.count(), 1)

        eric = self.create_user('eric')
        self.create_like(eric, self.comment)
        self.assertEqual(self.comment.like_set.count(), 2)