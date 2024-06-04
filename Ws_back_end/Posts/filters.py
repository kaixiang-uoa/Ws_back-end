from django_filters import rest_framework as filters
from .models import Post

class PostFilter(filters.FilterSet):
    title = filters.CharFilter(field_name='title', lookup_expr='icontains')
    author = filters.CharFilter(field_name='author__username', lookup_expr='icontains')
    date = filters.DateFilter(field_name='created_at', lookup_expr='date')
    tags = filters.CharFilter(field_name='tags__tag_name', lookup_expr='icontains')

    class Meta:
        model = Post
        fields = ['title', 'author', 'date', 'tags']
