from Products.PluggableAuthService import registerMultiPlugin
from AccessControl.Permissions import add_user_folders

from plugin import ExternalAuthPlugin, manage_add


def initialize(context):
    """Initializer called when used as a Zope 2 product."""
    registerMultiPlugin(ExternalAuthPlugin.meta_type)
    context.registerClass(ExternalAuthPlugin, permission=add_user_folders,
                          constructors=(manage_add,),
                          visibility=None)

