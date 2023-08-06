'''Helpers to use with cmf quick installer tool.
This use uninstall profiles which works without CMFCore except for the
contents which are not in is only available
with CMFCore'''

def pas_plugin_uninstall(product_name):
    ''' a decorator to use in extension module

    @pas_plugin_uninstall
    def uninstall(context):
        # do something after uninstall
        return msg + '\nplugin uninstalled'
    '''
    def pas_plugin_for_product(method):
        def pas_plugin_profile(context):
            from Products.CMFCore.utils import getToolByName
            qi = getToolByName(context, 'portal_quickinstaller')
            profile = qi.getInstallProfile(product_name)['id'] + ' - uninstall'
            context.portal_setup.runAllImportStepsFromProfile('profile-%s'
                                                             % profile)
            msg = method(context)
            return msg
        return pas_plugin_profile
    return pas_plugin_for_product

