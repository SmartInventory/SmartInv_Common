from rest_framework.permissions import IsAuthenticated


class ActionBasedPermission(IsAuthenticated):
    """
    Grant or deny access to a view, based on a mapping in view.action_permissions
    https://stackoverflow.com/a/47528633
    """

    def has_permission(self, request, view):
        for klass, actions in getattr(view, "action_permissions", {}).items():
            if view.action in actions:
                return klass().has_permission(request, view)
        return False
