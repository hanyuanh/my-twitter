from rest_framework import serializers
from tweets.models import Tweet
from accounts.api.serializers import UserSerializerForTweet

# ModelSerializer: set the properties in the fields, the serializer will auto
# gen the related variables in the program
class TweetSerializer(serializers.ModelSerializer):
    user = UserSerializerForTweet()
    # If user is not defined, user generated by ModelSerializer will be returned
    # as integer. It shows up that serializers(e.g. fields here) can be embedded
    # in serializers(ModelSerializer)

    class Meta:
        model = Tweet
        fields = ('id', 'user', 'created_at', 'content')


class TweetSerializerForCreate(serializers.ModelSerializer):
    content = serializers.CharField(min_length=6, max_length=140)

    class Meta:
        model = Tweet   #define which model is used (Tweet)
        fields = ('content',)   # access to content only

    def create(self, validated_data):
        # How can we get user here?
        # the
        user = self.context['request'].user
        content = validated_data['content']
        tweet = Tweet.objects.create(user=user, content=content)
        return tweet