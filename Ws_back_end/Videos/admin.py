from django.contrib import admin
from .models import Video

@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'src', 'thumbnail')
    search_fields = ('title',)
    readonly_fields = ('thumbnail',)  

    def get_readonly_fields(self, request, obj=None):
        if obj: 
            return self.readonly_fields
        return self.readonly_fields + ('thumbnail',)  
