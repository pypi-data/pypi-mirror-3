#    Copyright (C) 2003-2010  Corporation of Balclutha and contributors.
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
import AccessControl, AccessControl
from AccessControl.Permissions import view

add_merchant_service = 'BastionBanking: Add'
add_bank_service     = 'BastionBanking: Add'
manage_bastionbanking = 'BastionBanking: Manage'
operate_bastionbanking = 'BastionBanking: Operate'

def setDefaultRoles(permission, roles, object,acquire=1):
    # Make sure that a permission is registered with the given roles.
    registered = AccessControl.Permission._registeredPermissions
    if not registered.has_key(permission):
        registered[permission] = 1
        Products.__ac_permissions__=(
            Products.__ac_permissions__+((permission,(),roles),))
        mangled = AccessControl.Permission.pname(permission)
        setattr(Globals.ApplicationDefaultPermissions, mangled, roles)

    # Get the current roles with the given permission, so
    # that we don't overwrite them. We basically need to
    # merge the current roles with the new roles to be
    # assigned the given permission.
    current = object.rolesOfPermission(permission)
    roles = list(roles)
    for dict in current:
        if dict.get('selected'):
            roles.append(dict['name'])
    object.manage_permission(permission, roles, acquire)

def securityPolicy(bastionservice):
    """
    set up a default security policy for a BastionBank or BastionMerchant service

    presently, this just turns off view permission ...
    """
    setDefaultRoles(view, ('Manager',), bastionservice, 0)

