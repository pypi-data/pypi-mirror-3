from Products.CMFCore.DirectoryView import registerDirectory
GLOBALS = globals()
registerDirectory('skins', GLOBALS)

from zope.i18nmessageid import MessageFactory
PermissionComprehensibleMessageFactory = MessageFactory('PermissionComprehensible')

from Products.PythonScripts.Utility import allow_module

allow_module('Products.PermissionComprehensible.permissions_for_role_hack')
