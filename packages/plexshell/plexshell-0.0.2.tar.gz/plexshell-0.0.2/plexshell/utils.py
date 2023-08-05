from httplib import MOVED_PERMANENTLY, OK
import sys


class PlexError(Exception):
    ''' Exception raised when a server error is detected '''
    pass


class Colors:
    Blue = '\033[94m'
    Green = '\033[92m'
    Red = '\033[91m'
    EndC = '\033[0m'


def colorize(string, color):
    return color + string + Colors.EndC


def parse_address(address, connection):
    if not address.startswith("http://"):
        return connection.host, connection.port, address
    address = address.replace("http://", "")
    host, port = address.split("/")[0].split(":")
    return host, port, address.replace("%s:%s" % (host, port), "")


def chunked_read(response, chunk_size = 4096, progress = False):
    result = ""
    bytes_read = 0
    while True:
        chunk = response.read(chunk_size)
        bytes_read += len(chunk)
        result += chunk
        if progress:
            sys.stdout.write("\rread: %s bytes" % bytes_read)
            sys.stdout.flush()
        if not chunk:
            break
    return result


def get(conn, path, error_msg, progress = False):
    conn.request("GET", path)
    response = conn.getresponse()
    if response.status == MOVED_PERMANENTLY:
        location = response.getheader("location")
        print "redirected: %s" % location
        host, port, address = parse_address(location, conn)
        conn = HTTPConnection(host, port)
        return get(conn, address, error_msg, progress = progress)
    elif not response.status == OK:
        if error_msg:
            print "%s: %s" % (error_msg, response.reason)
        return None
    return chunked_read(response, progress = progress)
