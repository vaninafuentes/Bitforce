from rest_framework.permissions import BasePermission


class IsAdminGymUser(BasePermission):
    """
    Permiso que permite el acceso solo a usuarios con rol 'admin'.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.rol == 'admin'


class IsLimitedGymUser(BasePermission):
    """
    Permiso que permite el acceso solo a usuarios con rol 'limMerchant'.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.rol == 'limMerchant'