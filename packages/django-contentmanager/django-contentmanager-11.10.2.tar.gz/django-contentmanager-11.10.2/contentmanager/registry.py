from contentmanager.plugins import BasePlugin, create_permissions


class AlreadyRegistered(Exception):
    pass


class NotRegistered(Exception):
    pass


class ContentManagerRegistry(object):

    def __init__(self):
        self._registry = {} # plugin_type -> plugin class

    def register(self, plugin_or_iterable, autocreate=True):

        if issubclass(plugin_or_iterable, (BasePlugin,)):
            plugin_or_iterable = [plugin_or_iterable]

        for plugin in plugin_or_iterable:
            plugin_type = plugin.plugin_type()
            if self.is_registered(plugin_type):
                raise AlreadyRegistered('The plugin_type %s is already registered' % \
                                        plugin_type)
            # register
            if autocreate:
                from contentmanager.models import PluginType
                PluginType.objects.get_for_plugin_type(plugin_type)

            # Make sure plugins have some sort of descriptive name (at
            # least better than None)
            if not plugin.verbose_name:
                plugin.verbose_name = plugin.__name__

            # check whether permissions exist, if not create them
            create_permissions(plugin)
            self._registry[plugin_type] = plugin

    def unregister(self, block_or_iterable, autodelete=False):

        if issubclass(plugin_or_iterable, BasePlugin):
            plugin_or_iterable = [plugin_or_iterable]

        for plugin in plugin_or_iterable:
            plugin_type = plugin.plugin_type()
            if self.is_registered(plugin_type):
                raise NotRegistered('The plugin_type "%s: is not registered' % \
                                    plugin_type)
            # unregister
            del self._registry[plugin_type]
            if autodelete:
                from contentmanager.models import PluginType
                PluginType.objects.get_for_plugin_type(plugin_type).delete()

    def get_plugin(self, plugin_type):
        if self.is_registered(plugin_type):
            return self._registry[plugin_type]
        raise NotRegistered('The plugin_type "%s" is not registered' % \
                            plugin_type)

    def is_registered(self, plugin_type):
        return plugin_type in self._registry

    def cacheable(self, plugin_type):
        """
        Shortcut to cacheable for a plugin_type
        """
        return self.get_plugin(plugin_type).cacheable

# This global object represents the default contentmanager register.
registry = ContentManagerRegistry()
