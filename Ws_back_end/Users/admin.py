from django.contrib import admin
from .models import Ws_User, UserType, UserRelation, ProfessorAvailability

class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'user_type_name', 'is_approved', 'needs_review', 'is_active']
    list_filter = ['is_approved', 'needs_review', 'is_active', 'user_type__type_name'] 
    search_fields = ['username', 'email','user_type__type_name','phone_number'] 
    actions = ['approve_users', 'reject_users']

    def user_type_name(self, obj):
        return obj.user_type.type_name
    user_type_name.short_description = 'User Type'
    user_type_name.admin_order_field = 'user_type__type_name'

    def approve_users(self, request, queryset):
        queryset.update(is_approved=True, needs_review=False, is_active=True)
    approve_users.short_description = "Approve selected users"

    def reject_users(self, request, queryset):
        queryset.update(needs_review=True, is_approved=False,is_active=False)
    reject_users.short_description = "Reject selected users"


class ProfessorAvailabilityInline(admin.TabularInline):
    model = ProfessorAvailability
    extra = 1

class ProfessorAvailabilityAdmin(admin.ModelAdmin):
    list_display = ('professor', 'start_time', 'end_time')
    search_fields = ['professor__username', 'start_time', 'end_time']

admin.site.register(ProfessorAvailability, ProfessorAvailabilityAdmin)
admin.site.register(Ws_User, UserAdmin)
admin.site.register(UserRelation)
admin.site.register(UserType)
