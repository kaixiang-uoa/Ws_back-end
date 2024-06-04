from django.contrib import admin
from .models import Event, EventImage, UserEvent

class EventsAdmin(admin.ModelAdmin):
    list_display = ['title', 'date', 'location', 'description', 'organizer_name', 'is_approved', 'status']
    list_filter = ['is_approved', 'status']  
    search_fields = ['title', 'organizer__username', 'location', 'description']
    actions = ['approve_events', 'reject_events']

    def organizer_name(self, obj):
        return obj.organizer.username  
    organizer_name.short_description = 'Organizer Name'

    def approve_events(self, request, queryset):
        queryset.update(is_approved=True, status='approved')
    approve_events.short_description = "Approve selected events"

    def reject_events(self, request, queryset):
        queryset.update(is_approved=False, status='rejected')
    reject_events.short_description = "Reject selected events"

admin.site.register(Event, EventsAdmin)
admin.site.register(EventImage)
admin.site.register(UserEvent)
