# Copied and adapted from AccessControl/Role.py/permission_settings, which is under the ZPL 2.1

from AccessControl.Permission import Permission
from Products.CMFCore.utils import getToolByName
from AccessControl.PermissionRole import rolesForPermissionOn


def pc_get_permissions_for_role(self, role):
    # self in thise case is context
    result = []
    membership = getToolByName(self, 'portal_membership')
    user = membership.getAuthenticatedMember()
    assert user.hasRole('Manager')

    permissions = self.ac_inherited_permissions(1)

    for p in permissions:
        name, value = p[:2]
        p=Permission(name,value,self)
        all_permitted_roles=rolesForPermissionOn(name, self)
        all_acquired_roles = p.getRoles()
        if role in all_permitted_roles:
            d={'name': name,
               'acquire': isinstance(all_acquired_roles, list),
              }
            result.append(d)
    return result
