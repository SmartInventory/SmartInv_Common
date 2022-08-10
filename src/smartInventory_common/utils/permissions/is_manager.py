from rest_framework.permissions import IsAuthenticated

from smartInventory_common.utils.users import UserRoles


class SmartInvIsManagerUser(IsAuthenticated):
    def has_permission(self, request, view):
        if super(SmartInvIsManagerUser, self).has_permission(request, view):
            return bool(
                request.user
                and (request.user.role == UserRoles.ADMINISTRATOR or request.user.role == UserRoles.MANAGER)
            )
        return False
