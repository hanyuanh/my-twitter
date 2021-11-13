from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from friendships.models import Friendship
from friendships.api.serializers import (
    FollowingSerializer,
    FollowerSerializer,
    FriendshipSerializerForCreate,
)
from django.contrib.auth.models import User
from utils.paginations import FriendshipPagination

class FriendshipViewSet(viewsets.GenericViewSet):
    # POST /api/friendships/1/follow is to follow the user with user_id=1
    # therefore queryset here needs to be User.objects.all()
    # If it uses Friendship.objects.all(), error return 404 Not Found
    # Because the actions of detail=True will auto call get_object(), which is
    # queryset.filter(pk=1) to look up the object
    serializer_class = FriendshipSerializerForCreate
    queryset = User.objects.all()
    pagination_class = FriendshipPagination

    @action(methods=['GET'], detail=True, permission_classes=[AllowAny])
    def followers(self, request, pk):
        friendships = Friendship.objects.filter(to_user_id=pk).order_by('-created_at')
        page = self.paginate_queryset(friendships)
        serializer = FollowerSerializer(page, many=True, context={'request': request})
        return self.get_paginated_response(serializer.data)

    @action(methods=['GET'], detail=True, permission_classes=[AllowAny])
    def followings(self, request, pk):
        friendships = Friendship.objects.filter(from_user_id=pk).order_by('-created_at')
        page = self.paginate_queryset(friendships)
        serializer = FollowingSerializer(page, many=True, context={'request': request})
        return self.get_paginated_response(serializer.data)

    # follow method is just for login user
    @action(methods=['POST'], detail=True, permission_classes=[IsAuthenticated])
    def follow(self, request, pk):
        # check if user with id+pk exists
        self.get_object()

        # /api/friendships/<pk>/follow/
        # special case: multiple click on follow because of network delay\
        serializer = FriendshipSerializerForCreate(data={
            'from_user_id': request.user.id,   # current user
            'to_user_id': pk,                  # the user I want to follow
        })
        # Another way to implement:
        # create a public method for the validation response
        # raise_400_if_serializer_is_not_valid(serializer)
        if not serializer.is_valid():
            return Response({
                "success": False,
                "message": "Please check input",
                "errors": serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)
        instance = serializer.save()
        return Response(
            FollowingSerializer(instance, context={'request':request}).data, # to know exactly who I follow
            status=status.HTTP_201_CREATED,
        )

    @action(methods=['POST'], detail=True, permission_classes=[IsAuthenticated])
    def unfollow(self, request, pk):
        self.get_object()   # raise 404 if no user with id=pk
        # pk is a str, need to convert to int
        if request.user.id == int(pk):
            return Response({
                'success': False,
                'message': 'You cannot unfollow yourself',
            }, status=status.HTTP_400_BAD_REQUEST)
        # https://docs.djangoproject.com/en/3.1/ref/models/querysets/#delete
        # delete() in Queryset returns 2 values: 1. the sum of data deleted, 2.
        # a hash table, which represents num of data deleted for each type
        # Why multiple types of data deleted> Because foreign key might have
        # set up cascade delete, in which case a certain property in A model is
        # foreign key of B model, on_delete=models.CASCADE. When some data in B
        # are deleted, the related A will be deleted. That's why CASCADE is
        # dangerous. Should use on_delete=models.SET_NULL instead.
        deleted, _ = Friendship.objects.filter(
            from_user=request.user,
            to_user=pk,
        ).delete()
        return Response({'success': True, 'deleted': deleted})

    def list(self, request):
        return Response({'message':'this is friendships home page'})