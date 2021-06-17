from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from comments.models import Comment
from comments.api.serializers import (
    CommentSerializer,
    CommentSerializerForCreate,
    CommentSerializerForUpdate,
)
from comments.api.permissions import IsObjectOwner
from utils.decorators import required_params


class CommentViewSet(viewsets.GenericViewSet):
    """
    Here only implement list, create, update, destroy
    doesn't implement retrieve(to search for one single comment) because of no
    necessity
    """
    # 在django rest framework 的UI界面，基于这个serializer去渲染表单
    serializer_class = CommentSerializerForCreate
    queryset = Comment.objects.all()
    filterset_fields = ('tweet_id',)

    # methods
    # POST /api/comments/ -> create
    # GET /api/comments/ -> list
    # GET /api/comments/1/ -> retrieve
    # DELETE /api/comments/1/ -> destroy
    # PATCH /api/comments/1/ -> partial_patch
    # PUT /api/comments/1/ -> update

    def get_permissions(self):
        # To instantiate an object, parens are needed
        # AllowAny() / IsAuthenticated()
        # not just class names like  AllowAny / IsAuthenticated
        if self.action == 'create':
            return [IsAuthenticated()]
        if self.action in ['update', 'destroy']:
            return [IsAuthenticated(), IsObjectOwner()]
        return [AllowAny()]

    @required_params(params=['tweet_id'])
    def list(self, request, *args, **kwargs):
        # tweet_id = request.query_params['tweet_id']
        # comments = Comment.objects.filter(tweet_id=tweet_id)
        # serializer = CommentSerializer(comments, many=True)
        # return ...
        queryset = self.get_queryset()
        # Here use prefetch_related('user') to reduce sql queries
        comments = self.filter_queryset(queryset)\
            .prefetch_related('user')\
            .order_by('created_at')
        serializer = CommentSerializer(comments, many=True)
        return Response(
            {'comments': serializer.data},
            status=status.HTTP_200_OK,
        )

    def create(self, request, *args, **kwargs):
        data = {
            'user_id': request.user.id,
            'tweet_id': request.data.get('tweet_id'),
            'content': request.data.get('content'),
        }
        # Here must have 'data=' to assign params to data
        # because the first default param is instance
        serializer = CommentSerializerForCreate(data=data)
        if not serializer.is_valid():
            return Response({
                'message': 'Please check input',
                'errors': serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)

        # the save() method would trigger create() method in serializer, click
        # into save() to see its implementation.
        comment = serializer.save()
        return Response(
            CommentSerializer(comment).data,
            status=status.HTTP_201_CREATED,
        )

    def update(self, request, *args, **kwargs):
        # get_object is a function wrapped by DRF. It will use filter id to
        # filter object out of queryset, raise 404 error when not found
        # There is no extra code needed
        comment = self.get_object()
        serializer = CommentSerializerForUpdate(
            instance=comment,
            data=request.data,
        )
        if not serializer.is_valid():
            raise Response({
                'message': 'Please check input'
            }, status=status.HTTP_400_BAD_REQUEST)
        # save() will trigger update() in serializer, click into save() to see
        # implementation
        # save() will trigger create() or update() based on whether instance
        # param is filled or not
        comment = serializer.save()
        return Response(
            CommentSerializer(comment).data,
            status=status.HTTP_200_OK,
        )

    def destroy(self, request, *args, **kwargs):
        comment = self.get_object()
        comment.delete()
        # In DRF, by default, destroy() returns status code = 204 no content
        # Here return success=True, just for frontend to make use of it to make
        # easier judgment that delete is succeed, return 200
        return Response({'success': True}, status=status.HTTP_200_OK)