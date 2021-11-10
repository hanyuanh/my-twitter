from rest_framework.permissions import BasePermission


class IsObjectOwner(BasePermission):
    """
    This Permission is to check whether obj.user is equal to request.user
    This class is for some general purpose. In future if this is being used,
    the src file can be placed in a shared directory
    Permission methods will be executed one by one
    - if action with detail=False, only has_permission be detected
    - if action with detail=True, has_permission and has_object_permission
        be detected
    If error, error message by default will show content in
        IsObjectOwner.message
    """
    message = "You do not have permission to access this object"

    def has_permission(self, request, view):
        return True

    def has_object_permission(self, request, view, obj):
        return request.user == obj.user