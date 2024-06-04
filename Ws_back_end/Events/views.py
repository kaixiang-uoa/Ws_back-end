# from .serializers import EventSerializer
# from .models import Event, UserEvent
# from rest_framework import viewsets, status, generics
# from rest_framework.views import APIView
# from rest_framework.permissions import IsAdminUser
# from rest_framework.response import Response
# from rest_framework.decorators import action
# from ApiManage.permissions import IsAuthorOrAdmin
# from rest_framework.permissions import IsAuthenticated
# from Users.serializers import UserSerializer
# from Users.models import Ws_User
# # from taggit.models import Tag
# from django.db.models import Q

# class EventViewSet(viewsets.ModelViewSet):
#     queryset = Event.objects.all()
#     serializer_class = EventSerializer
#     organizer = UserSerializer(read_only=True)

#     def get_permissions(self):
#         if self.action in ['approve', 'reject']:
#             self.permission_classes = [IsAdminUser]
#         elif self.action in ['destroy', 'update', 'partial_update']:
#             self.permission_classes = [IsAuthorOrAdmin]
#         return super().get_permissions()
    
#     def create(self, request, *args, **kwargs):
#         data = request.data.copy()
#         data['organizer'] = request.user.id
#         serializer = self.get_serializer(data=data)
#         serializer.is_valid(raise_exception=True)
#         self.perform_create(serializer)
#         headers = self.get_success_headers(serializer.data)
#         return Response({"detail": "Event created successfully. Please wait for approval."}, status=status.HTTP_201_CREATED, headers=headers)

#     def perform_create(self, serializer):
#         serializer.save(organizer=self.request.user)

#     # approve or reject event
#     @action(detail=True, methods=['post'], url_path='approve')
#     def approve(self, request, pk=None):
#         event = self.get_object()
#         event.is_approved = True
#         event.save()
#         return Response({'status': 'event approved'})

#     @action(detail=True, methods=['post'], url_path='reject')
#     def reject(self, request, pk=None):
#         event = self.get_object()
#         event.is_approved = False
#         event.save()
#         return Response({'status': 'event rejected'})
    
#     # delete event
#     def destroy(self, request, *args, **kwargs):
#         event = self.get_object()
#         self.check_object_permissions(request, event)  # Check object-level permissions
#         self.perform_destroy(event)
#         return Response({"detail": "Event successfully deleted."}, status=status.HTTP_200_OK)
    
#     def update(self, request, *args, **kwargs):
#         event = self.get_object()
#         self.check_object_permissions(request, event)  # Check object-level permissions
#         response = super().update(request, *args, **kwargs)
#         return Response({"detail": "Event successfully updated.", "data": response.data}, status=status.HTTP_200_OK)
    
#     def partial_update(self, request, *args, **kwargs):
#         event = self.get_object()
#         self.check_object_permissions(request, event)  # Check object-level permissions
#         response = super().partial_update(request, *args, **kwargs)
#         return Response({"detail": "Event successfully updated.", "data": response.data}, status=status.HTTP_200_OK)

    
#     # register and unregister for event
#     @action(detail=True, methods=['post'], url_path='register', permission_classes=[IsAuthenticated])
#     def register(self, request, pk=None):
#         event = self.get_object()
#         user = request.user
#         if UserEvent.objects.filter(user=user, event=event).exists():
#             return Response({'detail': 'Already registered for this event.'}, status=status.HTTP_400_BAD_REQUEST)
#         UserEvent.objects.create(user=user, event=event)
#         return Response({'detail': 'Successfully registered for the event.'}, status=status.HTTP_201_CREATED)

#     @action(detail=True, methods=['post'], url_path='unregister', permission_classes=[IsAuthenticated])
#     def unregister(self, request, pk=None):
#         event = self.get_object()
#         user = request.user
#         user_event = UserEvent.objects.filter(user=user, event=event).first()
#         if user_event:
#             user_event.delete()
#             return Response({'detail': 'Successfully unregistered from the event.'}, status=status.HTTP_200_OK)
#         return Response({'detail': 'You are not registered for this event.'}, status=status.HTTP_400_BAD_REQUEST)
    
# # list users registered for an event
# class EventRegisterUsersView(generics.GenericAPIView):
#     def get(self, request, event_id, *args, **kwargs):
#         try:
#             event = Event.objects.get(id=event_id)
#         except Event.DoesNotExist:
#             return Response({'error': 'Event not found'}, status=status.HTTP_404_NOT_FOUND)

#         user_events = UserEvent.objects.filter(event=event)
        
#         user_event_data = []
#         for user_event in user_events:
#             user_serializer = UserSerializer(user_event.user, fields=['id', 'username', 'email', 'user_type'])
#             user_event_data.append({
#                 'user': user_serializer.data,
#                 'registered_at': user_event.registered_at
#             })
        
#         return Response(user_event_data, status=status.HTTP_200_OK)
    

# # list events organized by a user
# class OrganizerEventsView(generics.GenericAPIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request, user_id, *args, **kwargs):
#         try:
#             user = Ws_User.objects.get(id=user_id)
#         except Ws_User.DoesNotExist:
#             return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

#         organized_events = Event.objects.filter(organizer=user)
#         serializer = EventSerializer(organized_events, many=True)

#         return Response(serializer.data, status=status.HTTP_200_OK)
    

# class EventSearchSuggestionView(APIView):

#     def get(self, request, *args, **kwargs):
#         query = request.query_params.get('q', '')
#         if not query:
#             return Response([])

        
#         events = Event.objects.filter(
#             Q(title__icontains=query)
#         ).values('id', 'title').distinct()

#         event_suggestions = [
#             {
#                 'id': event['id'],
#                 'title': event['title'],
#             }
#             for event in events
#         ]
#         return Response({'events': event_suggestions})
    
# class EventViewSet(viewsets.ModelViewSet):
#     queryset = Event.objects.all()
#     serializer_class = EventSerializer


from .serializers import EventSerializer, EventImageSerializer
from .models import Event, UserEvent, EventImage
from rest_framework import viewsets, status, generics,views
from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from ApiManage.permissions import IsAuthorOrAdmin
from rest_framework.parsers import MultiPartParser, FormParser
from Users.serializers import UserSerializer
from Users.models import Ws_User
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Q

class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    organizer = UserSerializer(read_only=True)
    
    def get_permissions(self):
        if self.action in ['approve', 'reject']:
            self.permission_classes = [IsAdminUser]
        elif self.action in ['destroy', 'update', 'partial_update']:
            self.permission_classes = [IsAuthorOrAdmin]
        return super().get_permissions()

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        # print("Received request data:", data)
        data['organizer'] = request.user.id
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        event = self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        if 'image' in data and data['image']:
            image_id = request.data['image']
            try:
                event_image = EventImage.objects.get(id=image_id)
                event_image.event = event
                event_image.save()
                event.image = event_image
                event.save()
            except EventImage.DoesNotExist:
                return Response({'detail': 'Image not found.'}, status=status.HTTP_404_NOT_FOUND)

        
        print("Event created with ID:", event.id)
        return Response({
            "detail": "Event created successfully. Please wait for approval.",
            "event_id": event.id
        }, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        return serializer.save(organizer=self.request.user)


    @action(detail=False, methods=['post'], url_path='register', permission_classes=[IsAuthenticated])
    def register(self, request):
        event_id = request.data.get('event_id')
        send_email = request.data.get('send_email', False)
        try:
            event = Event.objects.get(id=event_id)
        except Event.DoesNotExist:
            return Response({'detail': 'Event not found.'}, status=status.HTTP_404_NOT_FOUND)

        user = request.user
        if UserEvent.objects.filter(user=user, event=event).exists():
            return Response({'detail': 'Already registered for this event.'}, status=status.HTTP_400_BAD_REQUEST)
        UserEvent.objects.create(user=user, event=event)

        if send_email:
            self.send_confirmation_email(user, event)

        return Response({'detail': 'Successfully registered for the event.'}, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'], url_path='unregister', permission_classes=[IsAuthenticated])
    def unregister(self, request):
        event_id = request.data.get('event_id')
        try:
            event = Event.objects.get(id=event_id)
        except Event.DoesNotExist:
            return Response({'detail': 'Event not found.'}, status=status.HTTP_404_NOT_FOUND)

        user = request.user
        user_event = UserEvent.objects.filter(user=user, event=event).first()
        if user_event:
            user_event.delete()
            return Response({'detail': 'Successfully unregistered from the event.'}, status=status.HTTP_200_OK)
        return Response({'detail': 'You are not registered for this event.'}, status=status.HTTP_400_BAD_REQUEST)


    @action(detail=True, methods=['post'], url_path='approve')
    def approve(self, request, pk=None):
        event = self.get_object()
        event.status = 'approved'
        event.save()
        return Response({'status': 'event approved'})

    @action(detail=True, methods=['post'], url_path='reject')
    def reject(self, request, pk=None):
        event = self.get_object()
        event.status = 'rejected'
        event.save()
        return Response({'status': 'event rejected'})

    
    def send_confirmation_email(self, user, event):
        subject = f"Registration Confirmation for {event.title}"
        message = f"Hi {user.username},\n\nYou have successfully registered for {event.title} on {event.date} at {event.location}.\n\nThank you!"
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [user.email]

        send_mail(subject, message, from_email, recipient_list)


class EventRegisterUsersView(generics.GenericAPIView):
    def post(self, request, *args, **kwargs):
        event_id = request.data.get('event_id')
        try:
            event = Event.objects.get(id=event_id)
        except Event.DoesNotExist:
            return Response({'error': 'Event not found'}, status=status.HTTP_404_NOT_FOUND)

        user_events = UserEvent.objects.filter(event=event)

        user_event_data = []
        for user_event in user_events:
            user_serializer = UserSerializer(user_event.user, fields=['id', 'username', 'email', 'user_type'])
            user_event_data.append({
                'user': user_serializer.data,
                'registered_at': user_event.registered_at
            })

        return Response(user_event_data, status=status.HTTP_200_OK)

class OrganizerEventsView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id, *args, **kwargs):
        try:
            user = Ws_User.objects.get(id=user_id)
        except Ws_User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        organized_events = Event.objects.filter(organizer=user)
        serializer = EventSerializer(organized_events, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

class EventSearchSuggestionView(APIView):
    def get(self, request, *args, **kwargs):
        query = request.query_params.get('q', '')
        if not query:
            return Response([])

        events = Event.objects.filter(
            Q(title__icontains=query)
        ).values('id', 'title').distinct()

        event_suggestions = [
            {
                'id': event['id'],
                'title': event['title'],
            }
            for event in events
        ]
        return Response({'events': event_suggestions})

class EventImageUploadView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        if 'image' not in request.FILES:
            return Response({'image': ['This field is required.']}, status=status.HTTP_400_BAD_REQUEST)

        image = request.FILES['image']
        event_image = EventImage.objects.create(image_path=image)
        return Response({"image_id": event_image.id, "image_path": event_image.image_path.url}, status=status.HTTP_201_CREATED)

