from Products.PluggableAuthService import registerMultiPlugin
from AccessControl.Permissions import manage_users as ManageUsers

import plugin

registerMultiPlugin(plugin.EasyUserAuthentication.meta_type)

def initialize(context):

    context.registerClass(plugin.EasyUserAuthentication,
                         permission=ManageUsers,
                         constructors=(
                            plugin.manage_addEasyUserAuthenticationForm,
                            plugin.manage_addEasyUserAuthentication, )
                         )
