'''Install and uninstall step for PAS and Generic setup.
Uninstall profiles works by adding "remove" attributes in pas_plugins.xml but
the .delete part isn't implemented by GenericSetup.'''

import logging
from xml.dom.minidom import parseString

from Products.PluggableAuthService.PluggableAuthService import \
                                   PluggableAuthService
from Products.GenericSetup.interfaces import IFilesystemImporter
from Products.GenericSetup.utils import XMLAdapterBase

log_name = 'PluggableAuthService'
log = logging.getLogger(log_name)

def install_plugin(context):

    # acquire PAS
    obj = context.getSite()
    pas = getattr(obj, 'acl_users')
    if not isinstance(pas, PluggableAuthService):
        log.debug('acl_users is not as PAS, nothing to do.')
        return

    # Are we in a PAS plugin installation profile ?
    registerer = PasPluginsRegisterer(pas, context)
    f = registerer.name + registerer.suffix
    body = context.readDataFile(f)
    if not body:
        log.debug('Not a PAS plugin profile, nothing to do.')
        return

    # install PAS content
    if context.isDirectory('acl_users'):
        IFilesystemImporter(pas).import_(context, 'acl_users', True)

    # update plugin registry
    if body is not None:
        registerer.filename = f
        registerer.body = body
    log.info('Pas Plugin Profile imported.')


class PasPluginsRegisterer(XMLAdapterBase):

    name = 'pas_plugins'
    _LOGGER_ID = log_name

    def _importNode(self, node):
        """Import the object from the DOM node.
        """
        pas = self.context
        imp_context = self.environ

        del_ = pas._delObject
        ls = pas.objectIds
        activate_plug = pas.plugins.activatePlugin
        ls_plugs = pas.plugins.listPluginIds
        mv_up_plug = pas.plugins.movePluginsUp

        for c in (child for child in node.childNodes
                         if child.nodeName == 'plugin-type'):

            iface_mod, iface = c.getAttribute('interface').rsplit('.', 1)
            mod = __import__(iface_mod, fromlist=1)
            interface = getattr(mod, iface)

            for p in (plugin for plugin in c.childNodes
                              if plugin.nodeName == 'plugin'):
                id = p.getAttribute('id')

                if p.hasAttribute('remove'):
                    # this shoud be sufficient as pas _delOb remove plugin part
                    if id in ls():
                        del_(id)

                elif p.hasAttribute('insert-after'):
                    activate_plug(interface, id)
                    plugs = ls_plugs(interface)
                    after = p.getAttribute('insert-after')
                    if after != '*':
                        while plugs.index(id) - plugs.index(after) != 1:
                            mv_up_plug(interface, (id,))
                            plugs = ls_plugs(interface)

                elif p.hasAttribute('insert-before'):
                    activate_plug(interface, id)
                    plugs = ls_plugs(interface)
                    before = p.getAttribute('insert-before')
                    if before == '*':
                        if id not in plugs:
                            raise RuntimeError(str((plugs, id)))
                        while plugs.index(id) != 0:
                            mv_up_plug(interface, (id,))
                            plugs = ls_plugs(interface)
                    else:
                        while plugs.index(before) -  plugs.index(id) != 1:
                            mv_up_plug(interface, (id,))
                            plugs = ls_plugs(interface)

