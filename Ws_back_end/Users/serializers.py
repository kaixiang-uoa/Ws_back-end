from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import Ws_User, UserType, UserRelation, ProfessorAvailability
from taggit.serializers import TagListSerializerField, TaggitSerializer
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.sites.shortcuts import get_current_site
from django.conf import settings
from .tokens import account_activation_token

class DynamicFieldsModelSerializer(serializers.ModelSerializer):
    """
    A ModelSerializer that takes an additional `fields` argument that
    controls which fields should be displayed.
    """
    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)
        super().__init__(*args, **kwargs)

        if fields is not None:
            # Drop any fields that are not specified in the `fields` argument.
            allowed = set(fields)
            existing = set(self.fields.keys())
            for field_name in existing - allowed:
                self.fields.pop(field_name)

class UserTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserType
        fields = '__all__'

class ProfessorAvailabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfessorAvailability
        fields = ['start_time', 'end_time']

    def create(self, validated_data):
        validated_data['professor'] = self.context['request'].user
        return super().create(validated_data)
    
    def validate(self, data):
        start_time = data['start_time']
        end_time = data['end_time']

        if start_time >= end_time:
            raise serializers.ValidationError("End time must be after start time.")

        if ProfessorAvailability.objects.filter(professor=self.context['request'].user, start_time=start_time, end_time=end_time).exists():
            raise serializers.ValidationError("This time slot is already added.")

        return data

class ProfessorSerializer(TaggitSerializer, serializers.ModelSerializer):
    availability_set = ProfessorAvailabilitySerializer(many=True, read_only=True)
    tags = TagListSerializerField()
    following_count = serializers.SerializerMethodField()
    posts = serializers.SerializerMethodField()

    class Meta:
        model = Ws_User
        fields = [
            'id', 'username', 'email', 'tags', 'availability_set', 'avatar_path', 
            'phone_number', 'is_active', 'following_count', 'posts'
        ]
        read_only_fields = ['id', 'username', 'email']

    def get_following_count(self, obj):
        return obj.followers.count()

    def get_posts(self, obj):
        from Posts.serializers import PostSerializer
        posts = obj.posts.all()
        return PostSerializer(posts, many=True).data


class UserSerializer(DynamicFieldsModelSerializer):
    user_type = serializers.PrimaryKeyRelatedField(queryset=UserType.objects.all(), allow_null=True, required=False)
    document = serializers.FileField(required=False)
    tags = TagListSerializerField(required=False)
    availability_set = ProfessorAvailabilitySerializer(many=True, read_only=True)
    user_type_name = serializers.CharField(source='user_type.type_name', read_only=True)

    class Meta:
        model = Ws_User
        fields = '__all__'
        extra_kwargs = {
            'password': {'write_only': True, 'required': True},
            'is_approved': {'read_only': True},
            'needs_review': {'read_only': True}
        }

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user_type = validated_data.get('user_type')
        user = Ws_User(**validated_data)
        user.set_password(password)  

       
        user.is_active = False
        
        if user_type and user_type.type_name == "Normal_User":
            user.is_approved = True
            user.needs_review = False
        elif user_type and user_type.type_name == "Professor":
            user.is_approved = False
            user.needs_review = True
        elif user_type and user_type.type_name == "Admin":
            user.is_approved = True
            user.needs_review = False
            user.is_staff = True
            user.is_superuser = True
            user.is_active = True
        
        user.save()

        if 'document' in validated_data and user_type.type_name == 'Professor':
            user.document = validated_data['document']
            user.save()
            
        return user

class FollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserRelation
        fields = ['following']
        read_only_fields = ['follower']

    def validate(self, data):
        request = self.context.get('request')
        if not request:
            raise serializers.ValidationError("Request object not found in context.")
        
        follower = request.user
        following = data.get('following')
        if follower == following:
            raise serializers.ValidationError("You cannot follow yourself.")
        
        if UserRelation.objects.filter(follower=follower, following=following).exists():
            raise serializers.ValidationError("You are already following this user.")
        
        return data

    def create(self, validated_data):
        follower = self.context['request'].user
        following = validated_data.get('following')
        UserRelation.objects.create(follower=follower, following=following)
        
        return {
            "detail": "Successfully followed.",
            "is_following": True,
            "following_count": following.followers.count(),
            "follower_count": follower.following.count()
        }
    

class FollowListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ws_User
        fields = ['id', 'username', 'avatar_path']


class UpdateUserSerializer(TaggitSerializer, serializers.ModelSerializer):
    tags = TagListSerializerField(required=False, allow_null=True)

    class Meta:
        model = Ws_User
        fields = ['username', 'phone_number', 'avatar_path', 'documents', 'tags']
        read_only_fields = ['email']

    def update(self, instance, validated_data):
        user = self.context['request'].user
        user_type = user.user_type.type_name

        if user_type == 'Professor':
            if 'tags' in validated_data:
                instance.tags.set(*validated_data.pop('tags'))
            if 'documents' in validated_data:
                instance.documents = validated_data.pop('documents')
        
        if 'avatar_path' in validated_data:
            instance.avatar_path = validated_data.pop('avatar_path')

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class UserDetailSerializer(serializers.ModelSerializer):
    tags = serializers.SerializerMethodField()
    availability = serializers.SerializerMethodField()
    user_type_name = serializers.CharField(source='user_type.type_name', read_only=True)
    following_count = serializers.SerializerMethodField()
    followers_count = serializers.SerializerMethodField()
    is_following = serializers.SerializerMethodField()

    class Meta:
        model = Ws_User
        fields = [
            'id', 'username', 'email', 'user_type', 'user_type_name', 'avatar_path', 
            'phone_number', 'is_active', 'tags', 'availability', 'following_count', 
            'followers_count', 'is_following'
        ]

    def get_tags(self, obj):
        return obj.tags.names() if obj.tags else []

    def get_availability(self, obj):
        return obj.availability_set.all().values('start_time', 'end_time')

    def get_following_count(self, obj):
        return obj.following.count()

    def get_followers_count(self, obj):
        return obj.followers.count()

    def get_is_following(self, obj):
        request = self.context.get('request', None)
        if request and request.user.is_authenticated:
            return UserRelation.objects.filter(follower=request.user, following=obj).exists()
        return False

class PasswordChangeSerializer(serializers.Serializer):
    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate_current_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Current password is incorrect')
        return value

# class UserImage(serializers.ModelSerializer):
#     class Meta:
#         model = UserImage
#         fields = ['image_path']
