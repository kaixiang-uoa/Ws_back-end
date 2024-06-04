# bookings/admin.py
from django.contrib import admin
from .models import Booking

class BookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'professor', 'start_time', 'end_time', 'created_at', 'status')
    list_filter = ('status', 'created_at', 'start_time', 'end_time')
    search_fields = ('user__username', 'professor__username')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)

    def has_add_permission(self, request):
        
        return True

    def has_change_permission(self, request, obj=None):
        
        return True

    def has_delete_permission(self, request, obj=None):
        
        return True

    def has_view_permission(self, request, obj=None):
       
        return True

admin.site.register(Booking, BookingAdmin)
