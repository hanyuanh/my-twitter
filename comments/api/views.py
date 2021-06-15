from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from comments.models import Comment
from comments.api.serializers import (
    CommentSerializer,
    CommentSerializerForCreate,
)


class CommentViewSet(viewsets.ModelViewSet):
    """
    Here only implement list, create, update, destroy
    doesn't implement retrieve(to search for one single comment) because of no
    necessity
    """
    # 在django rest framework 的UI界面，基于这个serializer去渲染表单
    serializer_class = CommentSerializerForCreate
    queryset = Comment.objects.all()

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
        return [AllowAny()]

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