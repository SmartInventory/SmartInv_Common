from rest_framework.permissions import IsAuthenticated

from smartInventory_common.utils.users import UserRoles


class SmartInvIsSystem(IsAuthenticated):
    def has_permission(self, request, view):
        if super(SmartInvIsSystem, self).has_permission(request, view):
            return bool(
                request.user and (request.user.role == UserRoles.SYSTEM or request.user.role == UserRoles.ADMINISTRATOR)
            )
        return False
