from rest_framework.permissions import BasePermission

class IsAuthorOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        # Check if the user is an admin
        if request.user.is_staff:
            return True
        
        # Check if the object has an 'author' field
        if hasattr(obj, 'author'):
            return obj.author == request.user
        
        # Check if the object has an 'organizer' field
        if hasattr(obj, 'organizer'):
            return obj.organizer == request.user
        
        # If none of the above fields exist, deny permission
        return False