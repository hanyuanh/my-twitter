from accounts.models import UserProfile
from testing.testcases import TestCase


class UserProfileTests(TestCase):

    def test_profile_property(self):
        hanyuan = self.create_user('hanyuan')
        self.assertEqual(UserProfile.objects.count(), 0)
        p = hanyuan.profile
        self.assertEqual(isinstance(p, UserProfile), True)
        self.assertEqual(UserProfile.objects.count(), 1)