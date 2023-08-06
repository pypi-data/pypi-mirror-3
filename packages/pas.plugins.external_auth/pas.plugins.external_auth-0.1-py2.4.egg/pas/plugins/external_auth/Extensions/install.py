from pas.cmfextensions.update_steps.quick_installer import pas_plugin_uninstall

@pas_plugin_uninstall('pas.plugins.external_auth')
def uninstall(context):
    return 'external_auth uninstalled.'

