from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import User

edit_users = {}


class AccessManager:

    @staticmethod
    def check_edit_permission(user):
        AccessManager.init_access_control()

        # Check if user has permission to edit articles.
        if not (user.username in edit_users):
            # User is not in group 'TalgoxenEdit'.
            raise PermissionDenied(f"User {user.first_name} {user.last_name} ({user.username}) does not have edit permission.")

    @staticmethod
    def init_access_control():
        if len(edit_users) == 0:
            # Get all users with edit permission.
            editors = User.objects.filter(groups__name = 'TalgoxenEdit')
            for editor in editors:
                edit_users[editor.username] = editor

