from lxml import etree
from plexshell.commands import PlexCmd
from plexshell.model import Plugin
from plexshell.utils import get


class PluginCmd(PlexCmd):
    ''' Mixin that adds plugin related commands '''

    @classmethod
    def parse_plugins_response(cls, response):
        result = list()
        listing = etree.fromstring(response)
        for plugin_node in listing.findall(".//Plugin"):
            identifier = plugin_node.get("identifier")
            result.append(Plugin(identifier))
        return result

    def restart_plugin(self, plugin):
        print "Restarting plugin: %s" % plugin
        url = "/:/plugins/%s/restart" % plugin
        if get(self.conn, url, "Failed to restart plugin: ") is not None:
            print "Restart succeeded"

    def get_plugins(self, error_msg = None):
        response = get(self.conn, "/:/plugins/", error_msg)
        if not response:
            return None
        return self.parse_plugins_response(response)

    def help_restart(self):
        print 'Usage: restart plugin_identifier'
        print 'Restart the plugin with the given identifier'

    def help_plugins(self):
        print 'List all installed plugins'

    def complete_restart(self, text, line, begidx, endidx):
        plugins = self.get_plugins()
        return [p.identifier for p in plugins if p.identifier.startswith(text)]

    def do_plugins(self, s):
        plugins = self.get_plugins("Couldn't retrieve plugin list")
        for plugin in plugins:
            print plugin

    def do_restart(self, plugin_identifier):
        if not plugin_identifier:
            return self.help_restart()
        plugins = self.get_plugins("Couldn't retrieve plugin list")
        for plugin in plugins:
            if plugin.identifier == plugin_identifier:
                return self.restart_plugin(plugin)
        print "Unknown plugin: %s" % plugin_identifier

