from plexshell.commands import PlexCmd

class UpdateCmd(PlexCmd):
    ''' Mixin that provides a command to trigger the auto-updating process '''

    def do_update(self, s):
        print "Updating plugins"
        get(self.conn, "/system/appstore/updates/install", "Updating failed: ")

    def help_update(self):
        print "Intitiate the the Plex AppStore auto-update process"
