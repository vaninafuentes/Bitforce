from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsSystemAdmin(BasePermission):
    """
    Permite sólo a:
    - superusuarios, o
    - usuarios con rol='admin', o
    - usuarios que pertenecen al grupo 'admin'
    """
    message = "Sólo un administrador puede realizar esta acción."

    def has_permission(self, request, view):
        u = request.user
        if not u or not u.is_authenticated:
            return False
        if u.is_superuser:
            return True
        if getattr(u, "rol", None) == "admin":
            return True
        # opcional: por grupo
        try:
            return u.groups.filter(name="admin").exists()
        except Exception:
            return False


class IsAdminOrReadOnly(BasePermission):
    """
    Lectura para cualquiera; escritura sólo admin.
    Útil para endpoints list/retrieve abiertos y create/update/delete restringidos.
    """
    message = "Sólo un administrador puede modificar recursos."

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        u = request.user
        if not u or not u.is_authenticated:
            return False
        return (
            u.is_superuser
            or getattr(u, "rol", None) == "admin"
            or u.groups.filter(name="admin").exists()
        )


class IsAdminGymUser(BasePermission):
    """Compat: si querés mantener tu clase, pero con superuser/grupo."""
    message = "Requiere rol de administrador."

    def has_permission(self, request, view):
        u = request.user
        return bool(
            u
            and u.is_authenticated
            and (
                u.is_superuser
                or getattr(u, "rol", None) == "admin"
                or u.groups.filter(name="admin").exists()
            )
        )


class IsLimitedGymUser(BasePermission):
    """Sólo usuarios con rol 'limMerchant' (clientes/limitados)."""
    message = "Requiere rol limitado (limMerchant)."

    def has_permission(self, request, view):
        u = request.user
        return bool(u and u.is_authenticated and getattr(u, "rol", None) == "limMerchant")
