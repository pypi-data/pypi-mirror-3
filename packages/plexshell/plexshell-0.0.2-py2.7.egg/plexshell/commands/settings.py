from .directory import DirectoryCmd
from plexshell.model import Setting
from plexshell.utils import get, Colors, colorize
from lxml import etree
from urllib import quote


class SettingsCmd(DirectoryCmd):
    ''' Mixin that provides commands to edit user settings '''

    def help_save(self):
        print 'Save settings back to PMS'

    def help_set_value(self):
        print 'Usage: set name value'
        print 'Change a setting value'

    def help_get_value(self):
        print 'Usage: get name'
        print 'Print a setting value'

    def do_save(self, s):
        to_string = lambda s: "%s=%s" % (quote(s.identifier), quote(s.value))
        params = "&".join(map(to_string, self.settings))
        path = self.directory.path + "/set?" + params
        if get(self.conn, path, "Unable to save settings") is not None:
            self.dirty = False

    def do_set_value(self, string):
        components = string.split()
        if len(components) >= 2:
            name = components[0]
            value = " ".join(components[1:])
            self.update_setting(name, value)
        else:
            self.help_set()

    def do_get_value(self, name):
        if not len(name):
            return self.help_get()
        setting = self.get_setting(name)
        if not setting:
            print "Invalid setting: %s" % name
        else:
            print setting.value

    def do_cd(self, name):
        if self.dirty:
            print "Unsaved settings were lost"
        super(SettingsCmd, self).do_cd(name)
        return True

    def complete_set_value(self, text, line, begidx, endidx):
        return [s.name for s in self.settings if s.name.startswith(text)]

    def complete_get_value(self, text, line, begidx, endidx):
        return [s.name for s in self.settings if s.name.startswith(text)]

    def get_setting(self, name):
        return next((s for s in self.settings if s.name == name), None)

    def update_setting(self, name, value):
        setting = self.get_setting(name)
        if setting:
            setting.value = value
            self.dirty = True
        else:
            print "Invalid setting: %s" % name

    def __init__(self, conn, directory, stdin = None):
        super(SettingsCmd, self).__init__(conn, stdin = stdin)
        self.cwd = directory
        self.directory = directory
        self.settings = [s for s in self.list_directory(directory)
                         if isinstance(s, Setting)]
        self.dirty = False
        self.prompt_context = colorize(
            "%s[settings]" % self.directory, self.directory.color)
        self.update_prompt()

