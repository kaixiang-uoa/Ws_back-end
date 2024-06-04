from django.contrib import admin
from .models import Post, PostImage, Comment

class PostImageInline(admin.TabularInline):
    model = PostImage
    extra = 1

class PostAdmin(admin.ModelAdmin):
    inlines = [PostImageInline]

admin.site.register(Post)
admin.site.register(PostImage)
admin.site.register(Comment)