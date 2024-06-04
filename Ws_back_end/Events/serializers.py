from rest_framework import serializers
from .models import Event,UserEvent,EventImage
from Users.serializers import UserSerializer

class EventImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventImage
        fields = ['id', 'image_path']

class EventSerializer(serializers.ModelSerializer):
    organizer = UserSerializer(read_only=True)
    images = serializers.StringRelatedField(many=True, read_only=True)
    image = EventImageSerializer(read_only=True)
    class Meta:
        model = Event
        read_only_fields = ['is_approved', 'organizer']
        fields = '__all__'

class UserEventSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = UserEvent
        fields = ['user', 'registered_at']


