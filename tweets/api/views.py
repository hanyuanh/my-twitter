from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from tweets.api.serializers import (
    TweetSerializer,
    TweetSerializerForCreate,
    TweetSerializerForDetail,
)
from tweets.models import Tweet
from newsfeeds.services import NewsFeedService
from utils.decorators import required_params
from utils.paginations import EndlessPagination

# inherited from GenericViewSet
# try not to use ModelViewSet(you can CRUD in this view set), which is not what
# we want to provide to users
class TweetViewSet(viewsets.GenericViewSet):
    # rest framework will auto decide what your table should look like
    # based on the default value of serializer
    serializer_class = TweetSerializerForCreate
    #serializer_class = TweetSerializer
    queryset = Tweet.objects.all()
    pagination_class = EndlessPagination

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]     #AllowAny() is just for readability
        # list interface can be accessed by anyone
        # other interface cannot
        return [IsAuthenticated()]  #dont forget "()", means instantiate

    @required_params(params=['user_id'])
    def list(self, request, *args, **kwargs):
        # composite index: take user and created_at
        tweets = Tweet.objects.filter(
            user_id = request.query_params['user_id']
        ).order_by('-created_at')   #reverse order
        # get instance of the list of tweets
        tweets = self.paginate_queryset(tweets)
        serializer = TweetSerializer(
            tweets,
            context={'request': request},
            many=True,
        )
        # By default return dict
        return self.get_paginated_response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        tweet = self.get_object()
        serializer = TweetSerializerForDetail(
            tweet,
            context={'request': request},
        )
        return Response(serializer.data)

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
        return Response(
            TweetSerializer(tweet, context={'request': request}).data,
            status=201,
        )