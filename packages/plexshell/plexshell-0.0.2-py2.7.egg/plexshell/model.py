from utils import Colors
from lxml import etree
import re


class Node(object):
    @classmethod
    def create(self, node, parent):
        if node.tag == "Directory":
            if bool(node.get("search", 0)):
                return SearchDirectory(node, parent)
            elif bool(node.get("settings", 0)):
                return SettingsDirectory(node, parent)
            return Directory(node, parent)
        elif node.tag == "Track":
            return Track(node, parent)
        elif node.tag == "Artist":
            return Artist(node, parent)
        elif node.tag == "Setting":
            return Setting(node, parent)

    def __init__(self, node = None, parent = None, display_name = None):
        self._node = node
        self._parent = parent
        self._display_name = display_name

    def __str__(self):
        return self.display_name

    @property
    def node(self):
        return self._node

    @property
    def parent(self):
        return self._parent

    @property
    def display_name(self):
        return self._display_name or self.name

    @property
    def color(self):
        return Colors.EndC


class Directory(Node):
    @property
    def path(self):
        path = ""
        if self.node is not None:
            key = self.node.get('key').encode("utf8")
            path = key if key.startswith("/") else "%s/%s" % (
                self.parent.path, key)
        return path

    @property
    def name(self):
        name = "/"
        if self.node is not None:
            key = self.node.get('key').encode("utf8")
            name = (self.node.get("name", None) or
                    self.node.get('title')).encode("utf8")
        return name

    @property
    def display_path(self):
        if not self.parent:
            return "/"
        parent = self.parent.display_path
        return "%s/%s" % (parent if parent != "/" else "", self.name)

    @property
    def color(self):
        return Colors.Blue

    @property
    def backlink(self):
        if self.is_root():
            return None
        return Directory(self.node, self.parent, "..")

    def is_root(self):
        return self.name == "/"

    def is_parent_dir(self):
        return self.display_name == ".."

    def is_search_dir(self):
        return bool(self.node.get("search", 0))


class SearchDirectory(Directory):
    @property
    def name(self):
        name = super(SearchDirectory, self).name
        return re.sub("^Search ", "", name)


class Search(Directory):
    def __init__(self, node, parent, term, search_type, path):
        super(Search, self).__init__(node, parent, term)
        self.term = term
        self.search_type = search_type
        self.search_path = path

    @property
    def name(self):
        return self.term

    @property
    def path(self):
        return self.search_path

    @property
    def display_path(self):
        return "%s/%s/%s" % (
            self.parent.display_path, self.search_type, self.name)


class Artist(Node):
    def __str__(self):
        return self.name

    @property
    def name(self):
        return self.node.get("artist", None).encode("utf8")

    @property
    def path(self):
        parent_path = self.parent.path if self.parent else ""
        return "%s/%s" % (parent_path, self.node.get("key"))


class Track(Node):
    @property
    def name(self):
        return self.node.get("title", None)

    @property
    def path(self):
        return self.node.find(".//Media/Part").get("key")



class Plugin(object):
    def __init__(self, identifier):
        self.identifier = identifier

    def __str__(self):
        return self.identifier


class SettingsDirectory(Directory):
    @property
    def color(self):
        return Colors.Red


class Setting(Node):
    def __init__(self, node, parent):
        super(Setting, self).__init__(node, parent)
        self.identifier = node.get("id")
        self.label = node.get("label")
        self.value = node.get("value")

    def __str__(self):
        return "<setting id: '%s', label: '%s', value: '%s'>" % (
            self.identifier, self.label, self.value)

    @property
    def name(self):
        return self.label

    @property
    def color(self):
        return Colors.Red
