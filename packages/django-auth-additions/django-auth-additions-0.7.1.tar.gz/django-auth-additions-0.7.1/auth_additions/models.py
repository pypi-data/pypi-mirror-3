from functools import wraps

from django.db import models
from django.contrib.auth.models import User, Group, Permission
from django.core.validators import MaxLengthValidator

#####################
#                   #
#  Group additions  #
#                   #
#####################

# Groups need a ranking system.  Groups with a higher rank can be used to
# allow managers to see staff details, but not other managers (of the same
# rank, for instance).

try:
    Group._meta.get_field_by_name('rank')
except models.FieldDoesNotExist:
    Group.add_to_class('rank', models.PositiveSmallIntegerField(default=5))

# Ability to duplicate group, with all the same permissions.

def duplicate_group(group, new_name):
    """
    Duplicate a group, and all of it's permissions.
    Give it the provided name.
    
    Note: changing the original group's permission set will not update
    the duplicate group's permissions.
    """
    new_group = Group(name=new_name, rank=group.rank)
    new_group.save()
    new_group.permissions.add(*group.permissions.all())
    return new_group
    
Group.add_to_class('duplicate', duplicate_group)


#####################
#                   #
#  User additions   #
#                   #
#####################

# We can implement object-level permissions using the following method:
# 
# Put methods with the names 'viewable_by', 'editable_by' and 'deletable_by'
# onto your class that will be tested for those tasks.
# 
# A User object patched using the function below (and the four patches
# that follow) will be able to view/edit/delete/add objects of that class
# according to the method result.
# 
# If you pass in a class, instead of the object, it will only use the
# django permissions, rather than the method.
# 
# If the desired method cannot be found, it will revert back to the django permission.
#
# If a django permission cannot be found, the method has_perm(None) will result in 
# the object being visible to all people.

def can_do(*tasks):
    
    def inner(user, obj_or_class, data=None):
        for task in tasks:
            # If the object we are looking at has a bound method %sable_by, then
            # we want to call that.
            if hasattr(obj_or_class, "%sable_by" % task):
                function = getattr(obj_or_class, "%sable_by" % task)
                if function.im_self:
                    if data:
                        return function(user, data)
                    return function(user)
            # Get the permission object that matches.
            if hasattr(obj_or_class._meta, 'get_%s_permission' % task):
                perm_name = getattr(obj_or_class._meta, 'get_%s_permission' % task)()
                if perm_name:
                    perm = '%s.%s' % (
                        obj_or_class._meta.app_label, 
                        perm_name
                    )
                    return user.has_perm(perm)
        # If we could not find any matching permissions, then the user may do it.
        return True
    return inner

User.add_to_class('can_view', can_do('read', 'view'))
User.add_to_class('can_edit', can_do('edit', 'change', 'update'))
User.add_to_class('can_delete', can_do('remove', 'delete'))
User.add_to_class('can_create', can_do('create', 'add'))


User.add_to_class('name', property(lambda x: x.get_full_name()))


### Patches to existing columns.

def increase_field_length(field, length):
    if field.max_length < length:
        field.max_length = length
        for v in field.validators:
            if isinstance(v, MaxLengthValidator):
                v.limit_value = length

# Change name/username/email length(s) to 128.
for f_name in ('first_name', 'last_name', 'email', 'username'):
    field = User._meta.get_field_by_name(f_name)[0]
    increase_field_length(field, 128)


#############################
#                           #
#  Permission additions    #
#                           #
#############################

field = Permission._meta.get_field_by_name('name')[0]
increase_field_length(field, 128)