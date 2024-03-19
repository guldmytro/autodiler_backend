from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_staff


class IsAdminOrReadOrPost(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS \
                or request.method == 'POST':
            return True
        return request.user.is_staff


class CanPost(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method == 'POST':
            return True
        return False
