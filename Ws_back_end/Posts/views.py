import logging
from rest_framework import viewsets, status, permissions, generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.views import APIView
from .models import Post, Comment, PostImage
from django_filters.rest_framework import DjangoFilterBackend
from .serializers import PostSerializer, CommentSerializer
# from .filters import PostFilter
from ApiManage.permissions import IsAuthorOrAdmin
from rest_framework.decorators import action
from Users.models import UserRelation, Ws_User, UserType
from Users.serializers import UserDetailSerializer
from django.db.models import Q
from taggit.models import Tag, TaggedItem
from rest_framework.parsers import MultiPartParser, FormParser

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    filter_backends = [DjangoFilterBackend]
    permission_classes = [IsAuthorOrAdmin]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            self.permission_classes = [permissions.AllowAny]
        else:
            self.permission_classes = [IsAuthenticatedOrReadOnly]
        return super(PostViewSet, self).get_permissions()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        post_instance = serializer.instance
        response_data = {
            'title': post_instance.title,
            'created_at': post_instance.created_at,
            'author': {
                'username': post_instance.author.username,
                'email': post_instance.author.email,
                'user_type': post_instance.author.user_type.type_name
            },
            'status': post_instance.status,
            'tags': [tag.name for tag in post_instance.tags.all()],
            'comments': [],
            'images': [image.image_path.url for image in post_instance.images.all()]
        }

        return Response({"detail": "Post successfully created."},  status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        post = self.get_object()
        self.check_object_permissions(request, post)
        self.perform_destroy(post)
        return Response({"detail": "Post successfully deleted."}, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        post = self.get_object()
        self.check_object_permissions(request, post)
        serializer = self.get_serializer(post, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        post_instance = serializer.instance
        data = {
            'title': post_instance.title,
            'created_at': post_instance.created_at,
            'updated_at': post_instance.updated_at,
            'author': {
                'username': post_instance.author.username,
                'email': post_instance.author.email,
                'user_type': post_instance.author.user_type.type_name
            },
            'status': post_instance.status,
            'tags': [tag.name for tag in post_instance.tags.all()],
            'comments': [],
            'images': []
        }

        return Response({"detail": "Post successfully updated."}, status=status.HTTP_200_OK)

    def partial_update(self, request, *args, **kwargs):
        post = self.get_object()
        self.check_object_permissions(request, post)
        serializer = self.get_serializer(post, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        data = serializer.data
        return Response({"detail": "Post successfully partial_update."}, status=status.HTTP_200_OK)
    
    # get all posts by a user
    @action(detail=False, methods=['get'], url_path='user/(?P<user_id>[^/.]+)')
    def list_by_user(self, request, user_id=None):
        user_posts = Post.objects.filter(author_id=user_id)
        page = self.paginate_queryset(user_posts)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(user_posts, many=True)
        return Response(serializer.data)
    
    
    # get all posts followed by a user
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated], url_path='followed-posts')
    def followed_posts(self, request):
        user = request.user
        followed_users = UserRelation.objects.filter(follower=user).values_list('following', flat=True)
        followed_posts = Post.objects.filter(author_id__in=followed_users)
        
        page = self.paginate_queryset(followed_posts)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(followed_posts, many=True)
        return Response(serializer.data)

    # get all posts by normal users
    @action(detail=False, methods=['get'], url_path='normal-users-posts')
    def normal_users_posts(self, request):
        normal_user_type = UserType.objects.get(type_name='Normal_User')
        normal_user_posts = Post.objects.filter(author__user_type=normal_user_type)

        page = self.paginate_queryset(normal_user_posts)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(normal_user_posts, many=True)
        return Response(serializer.data)


    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def add_comment(self, request, pk=None):
        post = self.get_object()
        content = request.data.get('content')
        parent_comment_id = request.data.get('parent_comment_id')
        parent_comment = None

        if parent_comment_id:
            try:
                parent_comment = Comment.objects.get(id=parent_comment_id, post=post)
            except Comment.DoesNotExist:
                return Response({'detail': 'Parent comment not found.'}, status=status.HTTP_400_BAD_REQUEST)
    
        comment = Comment.objects.create(
            post=post,
            content=content,
            author=request.user,
            parent_comment=parent_comment
        )

        return Response({'detail': 'Comment successfully added.'}, status=status.HTTP_200_OK)



class FollowedUsersPostsViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        user = request.user
        followed_users = UserRelation.objects.filter(follower=user).values_list('following', flat=True)
        posts = Post.objects.filter(author__in=followed_users).order_by('-created_at')
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    

class PostSearchSuggestionView(APIView):
    # permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        query = request.query_params.get('q', '')
        if not query:
            return Response([])

        
        normal_users = Ws_User.objects.filter(user_type__type_name='Normal_User').values_list('id', flat=True)

        # search posts by title and author username
        posts = Post.objects.filter(
            Q(author_id__in=normal_users) & 
            (Q(title__icontains=query) | Q(author__username__icontains=query))
        ).values('id', 'title', 'author__id', 'author__username').distinct()


        author_ids = posts.values_list('author__id', flat=True).distinct()
        authors = Ws_User.objects.filter(id__in=author_ids).values('id', 'username')

        post_suggestions = [
            {
                'id': post['id'],
                'title': post['title'],
            }
            for post in posts
        ]

        author_suggestions = [
            {
                'id': author['id'],
                'username': author['username'],
            }
            for author in authors
        ]


        suggestions = {
            'posts': post_suggestions,
            'authors': author_suggestions,
        }

        return Response(suggestions)

class ArticleSearchSuggestionView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        query = request.query_params.get('q', '')
        if not query:
            return Response([])

        professors = Ws_User.objects.filter(user_type__type_name='Professor').values_list('id', flat=True)
        articles = Post.objects.filter(author_id__in=professors, title__icontains=query).values('id', 'title')

        return Response(list(articles))
    

class PostDetailView(generics.RetrieveAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        post = self.get_object()
        user = request.user
        is_following = UserRelation.objects.filter(follower=user, following=post.author).exists()
        post_data = PostSerializer(post).data
        author_data = UserDetailSerializer(post.author).data
        return Response({
            'post': post_data,
            'author': author_data,
            'is_following': is_following
        })

   
class PostImageUploadView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    # permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        if 'image' not in request.FILES:
            return Response({'image': ['This field is required.']}, status=status.HTTP_400_BAD_REQUEST)

        image = request.FILES['image']
        post_image = PostImage.objects.create(image_path=image)
        return Response({"image_id": post_image.id, "image_path": post_image.image_path.url}, status=status.HTTP_201_CREATED)
    
# user like or unlike a post    
# class ToggleLikePostView(APIView):
#     def post(self, request, pk, format=None):
#         try:
#             post = Post.objects.get(pk=pk)
#             user = request.user

#             if user in post.liked_by.all():
#                 post.liked_by.remove(user)
#                 post.likes -= 1
#                 message = 'unliked'
#             else:
#                 post.liked_by.add(user)
#                 post.likes += 1
#                 message = 'liked'
            
#             post.save()
#             return Response({'status': 'success', 'likes': post.likes, 'message': message}, status=status.HTTP_200_OK)
#         except Post.DoesNotExist:
#             return Response({'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)

# views.py


class ToggleLikePostView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk, format=None):
        try:
            post = Post.objects.get(pk=pk)
            user = request.user

            if user in post.liked_by.all():
                post.liked_by.remove(user)
                post.likes -= 1
                liked_by_user = False
                message = 'unliked'
            else:
                post.liked_by.add(user)
                post.likes += 1
                liked_by_user = True
                message = 'liked'
            
            post.save()
            return Response({
                'status': 'success',
                'likes': post.likes,
                'liked_by_user': liked_by_user,
                'message': message
            }, status=status.HTTP_200_OK)
        except Post.DoesNotExist:
            return Response({'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)
