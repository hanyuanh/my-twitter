from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from tweets.api.serializers import TweetSerializer, TweetSerializerForCreate
from tweets.models import Tweet
from newsfeeds.services import NewsFeedService

# inherited from GenericViewSet
# try not to use ModelViewSet(you can CRUD in this view set), which is not what
# we want to provide to users
class TweetViewSet(viewsets.GenericViewSet):
    # rest framework will auto decide what your table should look like
    # based on the default value of serializer
    serializer_class = TweetSerializerForCreate
    #serializer_class = TweetSerializer

    def get_permissions(self):
        if self.action == 'list':
            return [AllowAny()]     #AllowAny() is just for readability
        # list interface can be accessed by anyone
        # other interface cannot
        return [IsAuthenticated()]  #dont forget "()", means instantiate

    def list(self, request, *args, **kwargs):
        if 'user_id' not in request.query_params:
            return Response('missing user_id', status=400)
        # composite index: take user and created_at
        tweets = Tweet.objects.filter(
            user_id = request.query_params['user_id']
        ).order_by('-created_at')   #reverse order
        # get instance of the list of tweets
        serializer = TweetSerializer(tweets, many=True)
        # By default return dict
        return Response({'tweets': serializer.data})
    #@action(permission ...)
    def create(self, request):
        serializer = TweetSerializerForCreate(
            data=request.data,
            context={'request': request},
        )
        if not serializer.is_valid():
            return Response({
                "success": False,
                "message": "Please check input",
                "errors": serializer.errors,
            }, status=400)
        # otherwise we have a tweet instance here
        # save() will call create method in TweetSerializerForCreate
        tweet = serializer.save()
        NewsFeedService.fanout_to_followers(tweet)
        # Here I use TweetSerializer to show whats in the tweet
        # reminder: It is different from TweetSerializerForCreate
        return Response(TweetSerializer(tweet).data, status=201)