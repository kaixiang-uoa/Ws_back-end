from rest_framework import serializers
from .models import Booking
from Users.serializers import UserSerializer

class BookingSerializer(serializers.ModelSerializer):
    professor = UserSerializer(read_only=True)
    user = UserSerializer(read_only=True)
    additional_email = serializers.EmailField(required=False, allow_blank=True)

    class Meta:
        model = Booking
        fields = '__all__'
        read_only_fields = ['user', 'created_at', 'status']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        user = instance.user
        professor = instance.professor
        representation['user'] = {
            'User_id': user.id,
            'username': user.username,
            'email': user.email,
            'tags': [tag.name for tag in user.tags.all()]
        }
        representation['professor'] = {
            'Psychologist_id': professor.id,
            'username': professor.username,
            'email': professor.email,
            'tags': [tag.name for tag in professor.tags.all()]
        }
        return representation
