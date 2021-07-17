from rest_framework import permissions


class HasAdminRole(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_admin_role
