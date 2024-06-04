from rest_framework import serializers
from .models import Post, PostImage, Comment
from Users.serializers import UserDetailSerializer
from taggit.serializers import (TagListSerializerField, TaggitSerializer)


class PostImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostImage
        fields = '__all__'

class CommentSerializer(serializers.ModelSerializer):
    author = UserDetailSerializer(read_only=True)
    replies = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = '__all__'

    def get_replies(self, obj):
        replies = Comment.objects.filter(parent_comment=obj)
        return CommentSerializer(replies, many=True).data


class PostSerializer(serializers.ModelSerializer):
    images = PostImageSerializer(many=True, read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    tags = TagListSerializerField()
    author = UserDetailSerializer(read_only=True)
    liked_by_user = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ['id', 'title', 'content', 'created_at', 'updated_at', 'author', 'status', 'tags', 'comments', 'images','likes','liked_by','liked_by_user']
        read_only_fields = ['author', 'created_at', 'updated_at']

    def create(self, validated_data):
        tags_data = validated_data.pop('tags', [])
        post = Post.objects.create(**validated_data)
        if tags_data:
            post.tags.set(tags_data)
        return post

    def get_liked_by_user(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return request.user in obj.liked_by.all()
        return False

    def update(self, instance, validated_data):
        tags_data = validated_data.pop('tags', None)
        instance.title = validated_data.get('title', instance.title)
        instance.content = validated_data.get('content', instance.content)
        instance.status = validated_data.get('status', instance.status)
        instance.save()

        if tags_data is not None:
            instance.tags.set(tags_data)
        return instance