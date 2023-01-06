from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.user.is_staff


class IsCoach(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.user.role_id.name == 'coach' or request.user.is_staff


class IsOwnerOrAdminOrReadOnly(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    Assumes the model instance has an `owner` attribute.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        if obj.owner == request.user or request.user.is_staff:
            return True


class CheckRole:
    def is_coach(self, request):
        return request.user.role_id.name == 'coach'

    def is_admin(self, request):
        return request.user.is_staff

    def is_coach_or_admin(self, request):
        return request.user.role_id.name == 'coach' or request.user.is_staff

    def is_owner_or_admin(self, request, obj):
        if obj.id == request.user.id or request.user.is_staff:
            return True

    def is_report_owner_or_admin(self, request, obj):
        if obj.runner_id == request.user.id or request.user.is_staff:
            return True



check_role = CheckRole()
