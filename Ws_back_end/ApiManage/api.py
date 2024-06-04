from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.contrib.auth import authenticate
from rest_framework.exceptions import ValidationError
from Users.models import UserRelation, Ws_User
from Users.serializers import UserDetailSerializer
from rest_framework import serializers

class WsUserTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        request = self.context['request']
        email = attrs.get('email')  
        password = attrs.get('password')

        # Check if user exists with the given email
        try:
            print(email,password)
            user = Ws_User.objects.get(email=email)
        except Ws_User.DoesNotExist:
            raise ValidationError({'email': 'No user found with this email'})

        # Check if the password matches
        if not user.check_password(password):
            raise ValidationError({'password': 'Incorrect password'})

        user = authenticate(request=request, username=email, password=password)
        if user is None:
            raise ValidationError('No active account found with the given credentials')
        
        data = super().validate(attrs)
        
        # Serialize user data
        user_data = UserDetailSerializer(user).data
        
        # Add follow counts
        user_data.update({
            'followed': UserRelation.objects.filter(follower=user).count(),
            'following': UserRelation.objects.filter(following=user).count(),
        })

        data.update(user_data)
        return data

class WsUserTokenObtainPairView(TokenObtainPairView):
    serializer_class = WsUserTokenObtainPairSerializer

class WsUserTokenRefreshSerializer(TokenRefreshSerializer):
    user_id = serializers.IntegerField(required=False)

    def validate(self, attrs):
        data = super().validate(attrs)
        
        # Extract user_id from the validated data
        user_id = self.context['request'].data.get('user_id')

        if not user_id:
            raise serializers.ValidationError('User ID is required.')

        try:
            user = Ws_User.objects.get(pk=user_id)
        except Ws_User.DoesNotExist:
            raise serializers.ValidationError('User not found.')

        # Serialize user data
        user_data = UserDetailSerializer(user).data

        # Add follow counts
        user_data.update({
            'followed': UserRelation.objects.filter(follower=user).count(),
            'following': UserRelation.objects.filter(following=user).count(),
        })

        data.update(user_data)
        return data

class WsUserTokenRefreshView(TokenRefreshView):
    serializer_class = WsUserTokenRefreshSerializer