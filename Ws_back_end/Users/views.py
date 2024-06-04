from django.shortcuts import render, get_object_or_404
from .serializers import (
    UserSerializer,
    UserDetailSerializer,
    PasswordChangeSerializer, 
    UserTypeSerializer, 
    ProfessorAvailabilitySerializer, 
    UpdateUserSerializer,
    ProfessorSerializer, 
    FollowListSerializer
)
from .models import Ws_User, UserRelation, UserType, ProfessorAvailability
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics
from rest_framework.exceptions import ValidationError
from Events.models import UserEvent
from Events.serializers import EventSerializer
from taggit.models import Tag
from Posts.models import Post
from Posts.serializers import PostSerializer
from django.contrib.auth.tokens import default_token_generator  # for password reset
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from .tokens import account_activation_token
from django.conf import settings
from django.http import JsonResponse


class UserViewSet(viewsets.ModelViewSet):
    queryset = Ws_User.objects.all()
    serializer_class = UserSerializer

    def perform_create(self, serializer):
        user = serializer.save()
        
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = account_activation_token.make_token(user)
        activation_link = f"http://localhost:3000/activate/{uid}/{token}/"  

        mail_subject = 'Activate your account.'
        message = render_to_string('acc_active_email.html', {
            'user': user,
            'activation_link': activation_link
        })
        send_mail(mail_subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])

    @action(detail=True, methods=['get'], url_path='registered-events', permission_classes=[IsAuthenticated])
    def list_registered_events(self, request, pk=None):
        user = self.get_object()
        user_events = UserEvent.objects.filter(user=user)
        events = [ue.event for ue in user_events]
        serializer = EventSerializer(events, many=True)
        return Response(serializer.data)

class UserDetailView(generics.RetrieveAPIView):
    queryset = Ws_User.objects.all()
    serializer_class = UserDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
         
class UserTypeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = UserType.objects.all()
    serializer_class = UserTypeSerializer


class ProfessorAvailabilityViewSet(viewsets.ModelViewSet):
    queryset = ProfessorAvailability.objects.all()
    serializer_class = ProfessorAvailabilitySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(professor=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        start_time = serializer.validated_data['start_time']
        end_time = serializer.validated_data['end_time']

        # Check if the time slot already exists
        if ProfessorAvailability.objects.filter(professor=request.user, start_time=start_time, end_time=end_time).exists():
            return Response({
                "detail": "This time slot is already added."
            }, status=status.HTTP_400_BAD_REQUEST)

        # If not, create a new availability
        serializer.save(professor=request.user)
        headers = self.get_success_headers(serializer.data)
        return Response({
            "detail": "Availability time added successfully.",
            "status": status.HTTP_201_CREATED
        }, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=False, methods=['get'], url_path='availability-by-professor')
    def availability_by_professor(self, request):
        professor_id = request.query_params.get('professor_id')
        if not professor_id:
            return Response({'detail': 'Professor ID is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            professor = Ws_User.objects.get(id=professor_id)
        except Ws_User.DoesNotExist:
            return Response({'detail': 'Professor not found.'}, status=status.HTTP_404_NOT_FOUND)

        availabilities = ProfessorAvailability.objects.filter(professor=professor)
        serializer = ProfessorAvailabilitySerializer(availabilities, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    

class ProfessorViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ws_User.objects.filter(user_type__type_name='Professor')
    serializer_class = ProfessorSerializer
    # permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.prefetch_related('availability_set')


class ProfessorSearchSuggestionView(APIView):
    # permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        query = request.query_params.get('q', '')
        if not query:
            return Response([])

        # search professors
        professors = Ws_User.objects.filter(
            user_type__type_name='Professor',
            username__icontains=query
        ).values('id', 'username')

        # search tags
        tags = Tag.objects.filter(name__icontains=query).values('id', 'name')

        suggestions = {
            'professors': list(professors),
            'tags': list(tags),
        }

        return Response(suggestions)


class UserUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        user = request.user
        data = request.data.copy()
        
        tags = data.get('tags')
        if tags:
            try:
                tags = tags.split(',')
            except AttributeError:
                tags = []
            data['tags'] = tags

        serializer = UpdateUserSerializer(user, data=data, partial=True, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({"detail": "User profile successfully updated.", "data": serializer.data}, status=status.HTTP_200_OK)


class PasswordChangeView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, *args, **kwargs):
        user = request.user
        serializer = PasswordChangeSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response({"detail": "Password updated successfully"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProfessorPostListView(generics.ListAPIView):
    serializer_class = PostSerializer

    def get_queryset(self):
        professor_type = UserType.objects.get(type_name='Professor')
        return Post.objects.filter(author__user_type=professor_type)


class NormalUserPostListView(generics.ListAPIView):
    serializer_class = PostSerializer

    def get_queryset(self):
        normal_user_type = UserType.objects.get(type_name='Normal User')
        return Post.objects.filter(author__user_type=normal_user_type)


class FollowToggleView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        follower = request.user
        following_id = request.data.get('following')
        following = get_object_or_404(Ws_User, id=following_id)

        relation, created = UserRelation.objects.get_or_create(follower=follower, following=following)
        if not created:
            relation.delete()
            is_following = False
        else:
            is_following = True

        return Response({
            "detail": "Follow status toggled.",
            "is_following": is_following,
            "following_count": following.followers.count(),
            "follower_count": follower.following.count()
        }, status=status.HTTP_200_OK)

    def get(self, request, *args, **kwargs):
        follower = request.user
        following_id = request.query_params.get('following')
        if not following_id:
            raise ValidationError("Following ID is required.")
        following = get_object_or_404(Ws_User, id=following_id)

        is_following = UserRelation.objects.filter(follower=follower, following=following).exists()

        return Response({
            "is_following": is_following,
            "following_count": following.followers.count(),
            "follower_count": follower.following.count()
        })

class FollowingListView(generics.ListAPIView):
    serializer_class = FollowListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user_id = self.request.user
        return Ws_User.objects.filter(followers__follower_id=user_id)

class FollowerListView(generics.ListAPIView):
    serializer_class = FollowListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user_id = self.request.user
        return Ws_User.objects.filter(following__following_id=user_id)
    
class PasswordResetRequestView(APIView):
    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({"error": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = Ws_User.objects.get(email=email)
        except Ws_User.DoesNotExist:
            return Response({"error": "User with this email does not exist"}, status=status.HTTP_404_NOT_FOUND)

        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        reset_link = f"http://localhost:3000/reset-password/{uid}/{token}/"

        print(f"UID: {uid}")
        print(f"Token: {token}")


        send_mail(
            'Password Reset Request',
            f'Click the link to reset your password: {reset_link}',
            'from@example.com',
            [email],
            fail_silently=False,
        )
        return Response({"message": "Password reset link sent to email"}, status=status.HTTP_200_OK)
    

class PasswordResetView(APIView):
    def post(self, request, uidb64, token):
        new_password = request.data.get('password')
        if not new_password:
            return Response({"error": "Password is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = Ws_User.objects.get(pk=uid)
        except (Ws_User.DoesNotExist, ValueError, TypeError, OverflowError):
            return Response({"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)

        if default_token_generator.check_token(user, token):
            user.set_password(new_password)
            user.save()
            return Response({"message": "Password has been reset"}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)
        

def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = Ws_User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Ws_User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        return JsonResponse({'status': 'success', 'message': 'Account activated successfully!'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Activation link is invalid!'})
