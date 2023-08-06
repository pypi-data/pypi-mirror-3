# -*- coding: utf-8 -*-


class ObjectPermissionBackend(object):

    supports_inactive_user = False

    def authenticate(self, **credentials):
        return None

    def get_user(self, user_id):
        return None
    
    def has_perm(self, user_obj, perm, obj=None):
        if obj:
            field = getattr(obj, perm, None)
            if field:
                if not callable(field):
                    is_authorized = field
                else:
                    is_authorized = field(user_obj)
                return is_authorized
        return False
