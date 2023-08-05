from plexshell.commands import DirectoryCmd, PluginCmd, SettingsCmd, UpdateCmd
from plexshell.model import Track, Artist, Directory, Plugin, Setting
from plexshell.utils import Colors, colorize, parse_address, chunked_read, get


class PlexShell(DirectoryCmd, UpdateCmd, PluginCmd):
    ''' The command line interpretter '''

    def __init__(self, host, port, stdin = None):
        super(PlexShell, self).__init__(stdin = stdin)
        self.set_host(host, port)

    def help_get(self):
        print 'Get a resource'

    def complete_get(self, text, line, begidx, endidx):
        listing = self.list_directory(self.cwd)
        result = [node.name for node in listing
                  if node.name.startswith(text)
                  and isinstance(node, Track)]
        path = line.replace("get ", "")
        if not path:
            return [self.cwd.path]
        return [node.path.split("/")[-1]
                for node in listing if
                node.path.startswith(path)]

    def do_get(self, name):
        if not name:
            print self.list_directory(self.cwd, parse = False)
            return
        if name.startswith("/"):
            resource = get(self.conn, name, "Failed to get resource")
            if resource:
                print resource
            return
        track = self.get_track(name)
        if not track:
            print "%s does not exist" % name
            return
        print "get: %s" % track
        get(self.conn, track.path, "Failed to get track", progress = True)
