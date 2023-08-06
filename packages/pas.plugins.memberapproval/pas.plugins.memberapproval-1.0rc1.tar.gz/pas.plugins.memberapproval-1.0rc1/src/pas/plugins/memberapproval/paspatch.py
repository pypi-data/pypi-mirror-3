from Products.PluggableAuthService.PluggableAuthService import \
    PluggableAuthService, _SWALLOWABLE_PLUGIN_EXCEPTIONS

from pas.plugins.memberapproval.interfaces import IMemberApprovalPlugin

def userStatus(self, user_id):
    plugins = self._getOb('plugins')
    approvals = plugins.listPlugins(IMemberApprovalPlugin)
    for plugin_id, plugin in approvals:
        try:
            return plugin.userStatus( user_id )
        except _SWALLOWABLE_PLUGIN_EXCEPTIONS:
            pass
PluggableAuthService.userStatus = userStatus

def approveUser(self, user_id):
    plugins = self._getOb('plugins')
    approvals = plugins.listPlugins(IMemberApprovalPlugin)
    for plugin_id, plugin in approvals:
        try:
            return plugin.approveUser( user_id )
        except _SWALLOWABLE_PLUGIN_EXCEPTIONS:
            pass
PluggableAuthService.approveUser = approveUser

def disapproveUser(self, user_id):
    plugins = self._getOb('plugins')
    approvals = plugins.listPlugins(IMemberApprovalPlugin)
    for plugin_id, plugin in approvals:
        try:
            return plugin.disapproveUser( user_id )
        except _SWALLOWABLE_PLUGIN_EXCEPTIONS:
            pass
PluggableAuthService.disapproveUser = disapproveUser

