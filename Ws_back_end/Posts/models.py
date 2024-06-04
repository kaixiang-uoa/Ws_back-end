from django.db import models
from Users.models import Ws_User
from taggit.managers import TaggableManager
from django.conf import settings

class Post(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(Ws_User, on_delete=models.CASCADE, related_name='posts')
    status = models.CharField(max_length=20, choices=[('draft', 'Draft'), ('published', 'Published')], default='draft')
    tags = TaggableManager(blank=True)
    images = models.ManyToManyField('PostImage', related_name='posts', blank=True)
    likes = models.IntegerField(default=0)
    liked_by = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='liked_posts', blank=True)

    def __str__(self):
        return self.title

class PostImage(models.Model):
    image_path = models.ImageField(upload_to='post_images/', null=True, blank=True)

    def __str__(self):
        related_posts = self.posts.all()
        if related_posts:
            return f"{related_posts[0].title} Image"
        return "Orphan Image"
    
class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(Ws_User, on_delete=models.CASCADE, related_name='comments')
    parent_comment = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    likes = models.IntegerField(default=0)
    liked_by = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='liked_comments', blank=True)

    def __str__(self):
        return f"{self.author.username} - {self.post.title}"

    class Meta:
        ordering = ['-created_at']
