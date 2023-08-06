from django.contrib.auth.models import User

class EmailBackend(object):
    supports_object_permissions = False
    supports_anonymous_user = False
    supports_inactive_user = False
    
    def authenticate(self, username=None, password=None):
        if '@' in username:
            for user in User.objects.filter(email=username, is_active=True):
                if user.check_password(password):
                    return user
        return None
    
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

class CanDoBackend(object):
    supports_object_permissions = True
    supports_anonymous_user = True
    supports_inactive_user = False
    
    def authenticate(self, *args, **kwargs):
        return None
    
    def has_perm(self, user_obj, perm, obj=None):
        if not user_obj.is_authenticated():
            return False
        
        if obj is None:
            return False

        try:
            perm = perm.split('.')[-1].split('_')[0]
        except IndexError:
            return False
        
        return getattr(user_obj, 'can_%s' % perm)(obj)
