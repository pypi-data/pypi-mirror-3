from lxml import etree
from plexshell.commands import PlexCmd
from plexshell.model import Node, Directory, SettingsDirectory
from plexshell.model import Track, Artist, SearchDirectory, Search
from plexshell.utils import PlexError, get, colorize
from urllib import quote
import re


class DirectoryCmd(PlexCmd):
    ''' Plex directory related commands '''

    def __init__(self, conn = None, cwd = Directory(), *args, **kwargs):
        super(DirectoryCmd, self).__init__(conn, *args, **kwargs)
        self.cwd = cwd

    @classmethod
    def is_error_message(cls, node):
        return node.get("message", False)

    @classmethod
    def get_error_message(cls, node):
        return "%s: %s" % (node.get("header"), node.get("message"))

    @classmethod
    def check_error(cls, node):
        if node is not None and cls.is_error_message(node):
            raise PlexError(cls.get_error_message(node))

    @classmethod
    def parse_response(cls, response):
        node = etree.fromstring(response)
        cls.check_error(node)
        return node

    @classmethod
    def parse_directory_response(cls, response, directory):
        create_node = lambda child: Node.create(child, directory)
        return map(create_node, cls.parse_response(response))

    @property
    def cwd(self):
        return self._cwd

    @cwd.setter
    def cwd(self, cwd):
        self._cwd = cwd
        self.prompt_context = colorize(cwd.display_path, cwd.color)
        self.update_prompt()

    def list_directory(self, directory, error_msg = None, parse = True):
        response = get(self.conn, directory.path, error_msg)
        if not response or not parse:
            return response
        contents = self.parse_directory_response(response, directory)
        if directory.backlink:
            contents.insert(0, directory.backlink)
        return contents

    def get_node(self, directory, klass, predicate):
        items = self.list_directory(directory or self.cwd)
        test = lambda i: isinstance(i, klass) and predicate(i)
        return next((i for i in items if test(i)), None)

    def get_track(self, name, cwd = None):
        matcher = lambda n: n.name == name
        return self.get_node(cwd, Track, matcher)

    def get_directory(self, name, cwd = None):
        matcher = lambda n: (n.display_name or n.name) == name
        subdir = self.get_node(cwd, Directory, matcher)
        if subdir:
            if subdir.is_parent_dir():
                return subdir.parent
            return subdir

    def get_resource(self, name):
        if not name:
            return self.list_directory(self.cwd, parse = False)
        return super(DirectoryCmd, self).get_resource(name)

    def help_cd(self):
        print 'Change to a given directory'

    def help_ls(self):
        print 'List directory contents (defaults to current dir)'

    def help_pwd(self):
        print 'Print the path to the current directory'

    def complete_cd(self, text, line, begidx, endidx):
        components = line[3:].split("/")
        cwd = self.cwd
        for index, name in enumerate(components) or (0, ".."):
            if index == len(components) - 1:
                subdirs = self.list_directory(cwd)
                return [s.display_name for s in subdirs
                        if s.display_name.startswith(text)
                        and isinstance(s, (Directory))]
            cwd = self.get_directory(name, cwd)
            if not cwd:
                return []

    def do_pwd(self, s):
        print self.cwd.path or "/"

    def do_cd(self, name):
        if not len(name) or name == "/":
            self.cwd = Directory()
        for name in name.split("/"):
            if not self.cd_to_sibling(name):
                return

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

    def cd_to_search(self, search_directory):
        search = SearchCmd(self.conn, search_directory, stdin = self.stdin)
        search.cmdloop()
        self.cwd = search.cwd

    def cd_to_sibling(self, name):
        from .settings import SettingsCmd
        if not name:
            return
        original_directory = self.cwd
        directory = self.get_directory(name)
        if not directory:
            print "Invalid directory"
        elif isinstance(directory, SearchDirectory):
            self.cd_to_search(directory)
        elif isinstance(directory, SettingsDirectory):
            SettingsCmd(self.conn, directory, stdin = self.stdin).cmdloop()
        elif not self.list_directory(directory):
            print "Directory not found: %s" % directory
        else:
            self.cwd = directory
        return original_directory != directory

    def do_ls(self, name):
        directory = self.get_directory(name) if name else self.cwd
        listing = self.list_directory(directory, "Couldn't list directory")
        for subdir in listing or []:
            print colorize(subdir.display_name, subdir.color)

    do_l = do_ls


class SearchCmd(DirectoryCmd):
    def __init__(self, *args, **kwargs):
        super(SearchCmd, self).__init__(*args, **kwargs)
        self.prompt = "Enter search term: "

    def do_search(self, term):
        path = self.cwd.path + "&query=%s" % quote(term)
        response = get(self.conn, path, "Search failed")
        search_type = self.cwd.name
        self.cwd = self.cwd.parent # if parsing fails jump back to the parent
        self.cwd = Search(
            self.parse_response(response), self.cwd, term, search_type, path)

    def onecmd(self, line):
        try:
            self.do_search(line)
        except PlexError, e:
            print e
        return True
