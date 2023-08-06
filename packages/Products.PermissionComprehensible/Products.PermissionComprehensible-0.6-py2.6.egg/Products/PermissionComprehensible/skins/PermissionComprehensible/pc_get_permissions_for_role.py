##bind container=container
##bind context=context
##parameters=role
##title=Criterion Remove

from Products.PermissionComprehensible.permissions_for_role_hack import \
    pc_get_permissions_for_role

return pc_get_permissions_for_role(context, role)
